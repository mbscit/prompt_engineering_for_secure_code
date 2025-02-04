import React from 'react';
import useStore from '@store/store';
import { useTranslation } from 'react-i18next';
import { ChatInterface, ConfigInterface, MessageInterface } from '@type/chat';
import { getChatCompletion, getChatCompletionStream } from '@api/api';
import { parseEventSource } from '@api/helper';
import { limitMessageTokens, updateTotalTokenUsed } from '@utils/messageUtils';
import { _defaultChatConfig } from '@constants/chat';
import { officialAPIEndpoint } from '@constants/auth';

const useSubmit = () => {
  const { t, i18n } = useTranslation('api');
  const error = useStore((state) => state.error);
  const setError = useStore((state) => state.setError);
  const apiEndpoint = useStore((state) => state.apiEndpoint);
  const apiKey = useStore((state) => state.apiKey);
  const setGenerating = useStore((state) => state.setGenerating);
  const generating = useStore((state) => state.generating);
  const currentChatIndex = useStore((state) => state.currentChatIndex);
  const setChats = useStore((state) => state.setChats);

  const generateTitle = async (
    message: MessageInterface[]
  ): Promise<string> => {
    let data;
    try {
      if (!apiKey || apiKey.length === 0) {
        // official endpoint
        if (apiEndpoint === officialAPIEndpoint) {
          throw new Error(t('noApiKeyWarning') as string);
        }

        // other endpoints
        data = await getChatCompletion(
          useStore.getState().apiEndpoint,
          message,
          _defaultChatConfig
        );
      } else if (apiKey) {
        // own apikey
        data = await getChatCompletion(
          useStore.getState().apiEndpoint,
          message,
          _defaultChatConfig,
          apiKey
        );
      }
    } catch (error: unknown) {
      throw new Error(`Error generating title!\n${(error as Error).message}`);
    }
    return data.choices[0].message.content;
  };

  const handleSubmit = async () => {
    const chats = useStore.getState().chats;
    if (generating || !chats) return;

    const updatedChats: ChatInterface[] = JSON.parse(JSON.stringify(chats));

    updatedChats[currentChatIndex].messages.push({
      role: 'assistant',
      content: '',
    });

    setChats(updatedChats);
    setGenerating(true);

    try {
      let stream;
      if (chats[currentChatIndex].messages.length === 0)
        throw new Error('No messages submitted!');

      const messages = limitMessageTokens(
        chats[currentChatIndex].messages,
        chats[currentChatIndex].config.max_tokens,
        chats[currentChatIndex].config.model
      );
      if (messages.length === 0) throw new Error('Message exceed max token!');

      // no api key (free)
      if (!apiKey || apiKey.length === 0) {
        // official endpoint
        if (apiEndpoint === officialAPIEndpoint) {
          throw new Error(t('noApiKeyWarning') as string);
        }

        // other endpoints
        stream = await getChatCompletionStream(
          useStore.getState().apiEndpoint,
          messages,
          chats[currentChatIndex].config
        );
      } else if (apiKey) {
        // own apikey
        stream = await getChatCompletionStream(
          useStore.getState().apiEndpoint,
          messages,
          chats[currentChatIndex].config,
          apiKey
        );
      }

      if (stream) {
        if (stream.locked)
          throw new Error(
            'Oops, the stream is locked right now. Please try again'
          );
        const reader = stream.getReader();
        let reading = true;
        let partial = '';
        let inBlock = false;
        let blockContent = '';
        let blockLanguageChecked = false;
        let blockLanguage = '';
        let indent = '';  // To capture the initial indentation level
        let blockPlaceholder = (language: string = '', indent: string = '') =>
          '\n' + indent + '```' + (language ? language : 'text') + '\n' + indent + 'Snippet under review by Code Security Agent\n' + indent + '```\n';
        let backticks = '';
        while (reading && useStore.getState().generating) {
          const { done, value } = await reader.read();
          const result = parseEventSource(
            partial + new TextDecoder().decode(value)
          );
          partial = '';
          if (result === '[DONE]' || done) {
            reading = false;
          } else if (useStore.getState().codeSecurityAgent) {
            await result.reduce(async (outputPromise, curr) => {
              let output = '';
              await outputPromise; // Ensure the promise chain is maintained

              if (typeof curr === 'string') {
                partial += curr;
              } else {
                let content = curr.choices[0]?.delta?.content ?? null;
                if (content) {
                  const updatedChats = JSON.parse(JSON.stringify(useStore.getState().chats));
                  const updatedMessages = updatedChats[currentChatIndex].messages;

                  // Handle backticks in the content
                  for (let i = 0; i < content.length; i++) {
                    if (content[i] === '`') {
                      backticks += '`';
                    } else if (backticks.length < 3) {
                      backticks = '';
                    }
                  }

                  if (backticks && backticks.length == 3) {
                    if (inBlock) {
                      // End of a code block
                      blockContent += content.slice(0, content.indexOf('`'));
                      let improvedCode = await improveCodeSecurity(
                        chats[currentChatIndex].config,
                        blockContent,
                        blockLanguage,
                      );

                      const indentedImprovedCode = improvedCode.split('\n').map(line => indent + line).join('\n');
                      const codeBlock = indent + '```' + (blockLanguage ? blockLanguage : '') + '\n' + indentedImprovedCode + '\n' + indent + '```';
                      updatedMessages[updatedMessages.length - 1].content = updatedMessages[updatedMessages.length - 1].content.replace(blockPlaceholder(blockLanguage, indent), codeBlock);
                      setChats(updatedChats);
                      output += content.slice(content.lastIndexOf('`') + 1);
                      inBlock = false;
                      blockContent = '';
                      blockLanguage = '';
                      blockLanguageChecked = false;
                      backticks = '';
                    } else {
                      // Start of a code block
                      inBlock = true;

                      const lines = (updatedMessages[updatedMessages.length - 1].content + content.slice(0, content.indexOf('`'))).split('\n');
                      // Capture initial indentation from current content line
                      if (lines.length > 1) {
                        const match = lines[lines.length - 1].match(/^\s*/);
                        if (match) {
                          indent = match[0]; // Extract leading spaces
                        }
                      }

                      updatedMessages[updatedMessages.length - 1].content += content.slice(0, content.indexOf('`')) + blockPlaceholder('', indent);
                      setChats(updatedChats);
                      blockContent = content.slice(content.lastIndexOf('`') + 1);
                      backticks = '';
                    }

                  } else {
                    if (!blockLanguageChecked && inBlock) {
                      if (content.indexOf('\n') > -1) {
                        blockLanguage = blockLanguage + content.slice(0, content.indexOf('\n')).trim();
                        content = content.slice(content.indexOf('\n') + 1);
                        blockLanguageChecked = true;
                        if (blockLanguage) {
                          updatedMessages[updatedMessages.length - 1].content = updatedMessages[updatedMessages.length - 1].content.replace(blockPlaceholder('', indent), blockPlaceholder(blockLanguage, indent));
                          setChats(updatedChats);
                        }
                      } else {
                        blockLanguage = blockLanguage + content;
                        content = '';
                      }
                    }
                    if (!inBlock) {
                      output += content;
                    } else if (blockLanguageChecked) {
                      blockContent += content;
                    }
                  }

                  if (!inBlock) {
                    updatedMessages[updatedMessages.length - 1].content += output;
                    setChats(updatedChats);
                  }
                }
              }
            }, Promise.resolve());

          } else {
            const resultString = result.reduce((output: string, curr) => {
              if (typeof curr === 'string') {
                partial += curr;
              } else {
                const content = curr.choices[0]?.delta?.content ?? null;
                if (content) output += content;
              }
              return output;
            }, '');

            const updatedChats: ChatInterface[] = JSON.parse(
              JSON.stringify(useStore.getState().chats)
            );
            const updatedMessages = updatedChats[currentChatIndex].messages;
            updatedMessages[updatedMessages.length - 1].content += resultString;
            setChats(updatedChats);
          }
        }
        if (useStore.getState().generating) {
          reader.cancel('Cancelled by user');
        } else {
          reader.cancel('Generation completed');
        }
        reader.releaseLock();
        stream.cancel();
      }

      // update tokens used in chatting
      const currChats = useStore.getState().chats;
      const countTotalTokens = useStore.getState().countTotalTokens;

      if (currChats && countTotalTokens) {
        const model = currChats[currentChatIndex].config.model;
        const messages = currChats[currentChatIndex].messages;
        updateTotalTokenUsed(
          model,
          messages.slice(0, -1),
          messages[messages.length - 1]
        );
      }

      // generate title for new chats
      if (
        useStore.getState().autoTitle &&
        currChats &&
        !currChats[currentChatIndex]?.titleSet
      ) {
        const messages_length = currChats[currentChatIndex].messages.length;
        const assistant_message =
          currChats[currentChatIndex].messages[messages_length - 1].content;
        const user_message =
          currChats[currentChatIndex].messages[messages_length - 2].content;

        const message: MessageInterface = {
          role: 'user',
          content: `Generate a title in less than 6 words for the following message (language: ${i18n.language}):\n"""\nUser: ${user_message}\nAssistant: ${assistant_message}\n"""`,
        };

        let title = (await generateTitle([message])).trim();
        if (title.startsWith('"') && title.endsWith('"')) {
          title = title.slice(1, -1);
        }
        const updatedChats: ChatInterface[] = JSON.parse(
          JSON.stringify(useStore.getState().chats)
        );
        updatedChats[currentChatIndex].title = title;
        updatedChats[currentChatIndex].titleSet = true;
        setChats(updatedChats);

        // update tokens used for generating title
        if (countTotalTokens) {
          const model = _defaultChatConfig.model;
          updateTotalTokenUsed(model, [message], {
            role: 'assistant',
            content: title,
          });
        }
      }
    } catch (e: unknown) {
      const err = (e as Error).message;
      console.log(err);
      setError(err);
    }
    setGenerating(false);
  };

  return { handleSubmit, error };
};

function getCodeBlocks(response: string) {
  const regex = /```(\S*)\n(.*?)```/gs;

  const codeBlocks: Array<[string, string]> = [];
  const matches = response.matchAll(regex);

  // Iterate through all matches
  for (const match of matches) {
    // match[1] is the first capture group (\S*), containing the language
    // match[2] is the second capture group (.*?), containing the code
    codeBlocks.push([match[1], match[2]]);
  }
  return codeBlocks;
}

const improveCodeSecurity = async (config: ConfigInterface, code: string, language: string | undefined) => {
  const apiKey = useStore.getState().apiKey;
  const model = config.model
  const countTotalTokens = useStore.getState().countTotalTokens;

  if (code === '' || code === undefined) {
    return code;
  }

  let languageString = (language ? language + ' ' : '');

  let critiquePrompt = 'Review the following ' + languageString + ' code and find security problems with it: \n```' + languageString.trim() + '\n' + code + '\n```';
  let critiquePromptMessages: MessageInterface[] = [
    {
      role: 'user',
      content: critiquePrompt,
    },
  ];

  let critiqueCompletionObject = await getChatCompletion(
    useStore.getState().apiEndpoint,
    critiquePromptMessages,
    config,
    apiKey,
  );

  if(countTotalTokens) {
    updateTotalTokenUsed(
      model,
      critiquePromptMessages,
      critiqueCompletionObject
    );
  }

  let critique = critiqueCompletionObject.choices[0].message.content;

  console.log(critique);

  let improvementPrompt = 'Based on the critique: \n' + critique + '\nimprove the following snippet if needed. Otherwise return the unchanged code: \n```' + languageString + '\n' + code + '\n```';
  let improvementPromptMessages: MessageInterface[] = [
    {
      role: 'user',
      content: improvementPrompt,
    },
  ];

  let improvementCompletionObject = await getChatCompletion(
    useStore.getState().apiEndpoint,
    improvementPromptMessages,
    config,
    apiKey,
  );

  if(countTotalTokens) {
    updateTotalTokenUsed(
      model,
      improvementPromptMessages,
      improvementCompletionObject
    );
  }

  let improvement = improvementCompletionObject.choices[0].message.content;

  let codeBlocks = getCodeBlocks(improvement);
  if (language) {
    codeBlocks = codeBlocks.filter((block) => block[0] === language);
  }

  if (codeBlocks.length == 1) {
    return codeBlocks[0][1];
  } else {
    let retries = 0;
    while (retries < 3) {
      let response = await extractCodeWithGPT(config, critiquePromptMessages, improvement, language);
      let codeBlocks = getCodeBlocks(response);
      if (language) {
        codeBlocks = codeBlocks.filter((block) => block[0] === language);
      }
      if (codeBlocks.length == 1) {
        return codeBlocks[0][1];
      } else {
        retries += 1;
      }
    }
    console.error('Unable to get single code block after 3 retries');
    return code;
  }
};

async function extractCodeWithGPT(config: ConfigInterface, promptMessages: MessageInterface[], response: any, language: string | undefined): Promise<string> {
  const apiKey = useStore.getState().apiKey;
  const countTotalTokens = useStore.getState().countTotalTokens;


  let languageString = (language ? language + ' ' : '');

  let messages: MessageInterface[] = promptMessages;
  messages.push(
    {
      role: 'user',
      content: 'Only output the ' + languageString + 'code and nothing else.',
    });

  let extractionCompletionObject = await getChatCompletion(
    useStore.getState().apiEndpoint,
    messages,
    config,
    apiKey,
  );

  const model = config.model;
  if(countTotalTokens) {
    updateTotalTokenUsed(
      model,
      extractionCompletionObject,
      extractionCompletionObject
    );
  }


  return extractionCompletionObject.choices[0].message.content;


}

export default useSubmit;
