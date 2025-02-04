<h1 align="center"><b>Security-Aware ChatGPT</b></h1>


<p align="center">
    <a target="_blank"><img src="public/apple-touch-icon.png" alt="Better ChatGPT" width="100" /></a>
</p>

<h4 align="center"><b>ChatGPT, with more secure code.</b></h4>

## 👋🏻 Introducing Security Aware ChatGPT

Our fork of <a href="https://github.com/ztjhz/BetterChatGPT" target="_blank">Better ChatGPT</a> is introducing two new security-enhancing features.


# 🔥 Security Features
### Code Security Prefix
This feature can be enabled or disabled for each individual prompt. When enabled, it adds the a prefix the prompt:
<p align="center">
        <img src="assets/code_security_prefix.png" alt="landing" width=500 />
</p>
<span>This prefix reduced the number code vulnerabilities on average by 47% for gpt-4o-mini, and by 56% for gpt-4o (snapshot 2024-08-06) on the <a href="https://github.com/mbscit/prompt_engineering_for_secure_code_generation/prompt_benchmark/">Secure Prompt Benchmark</a>.</span>

### Code Security Agent (Experimental)
The "Code Security Agent" and can be enabled in the settings.
If enabled, markdown code-blocks in the response are intercepted.
<p align="center">
        <img src="assets/security_agent_review.png" alt="landing" width=500 />
</p>
The intercepted blocks are sent to the LLM for security-critique and improvement.  The code from the improvement response is then extracted and inserted back into the original answer.

Using the Code Security Agent with gpt-4o-2024-08-06 can reduce the number of vulnerabilities on average by 64.7\% without, and 68.7\% with the Code Security Prefix on the  <a href="https://github.com/mbscit/prompt_engineering_for_secure_code_generation/prompt_benchmark">Secure Prompt Benchmark</a>.

Since the Code Security Agent is interacting with the LLM multiple times, it can be very slow.
It can also make the code snippets overly verbose, and sometimes even break the code.
This feature is intended to gain insights into the implications of using this technique, and is therefore marked as experimental.


### Disclaimer
While these features can help reduce the number of code vulnerabilities, they are not a substitute for a security audit by a professional.  
The features are experimental and may not work as expected in all cases.

# Features form Better ChatGPT

Security-Aware ChatGPT comes with a bundle of amazing features from Better ChatGPT! Here are some of them:

- Proxy to bypass ChatGPT regional restrictions
- Prompt library
- Organize chats into folders (with colours)
- Filter chats and folders
- Token count and pricing
- ShareGPT integration
- Custom model parameters (e.g. presence_penalty)
- Chat as user / assistant / system
- Edit, reorder and insert any messages, anywhere
- Chat title generator
- Save chat automatically to local storage
- Import / Export chat
- Download chat (markdown / image / json)
- Sync to Google Drive
- Azure OpenAI endpoint support
- Multiple language support (i18n)

# 🛠️ Usage

1. Ensure that you have the following installed:

   - [node.js](https://nodejs.org/en/) (v14.18.0 or above)
   - [yarn](https://yarnpkg.com/) or [npm](https://www.npmjs.com/) (6.14.15 or above)

2. Clone this [repository](https://github.com/mbscit/prompt_engineering_for_secure_code_generation) by running `git clone https://github.com/mbscit/prompt_engineering_for_secure_code_generation.git`
3. Navigate into this directory by running `cd prompt_engineering_for_secure_code_generation/prompt_agent`
4. Run `yarn` or `npm install`, depending on whether you have yarn or npm installed.
5. Launch the app by running `yarn dev` or `npm run dev`

### Running it locally using docker compose
1. Ensure that you have the following installed:

   - [docker](https://www.docker.com/) (v24.0.7 or above)
      ```bash
      curl https://get.docker.com | sh \
      && sudo usermod -aG docker $USER
      ```

2. Build the docker image
   ```
   docker compose build
   ```

3. Build and start the container using docker compose
   ```
   docker compose build
   docker compose up -d
   ```

4. Stop the container
   ```
   docker compose down
   ```

# ❤️ Contributors of Better ChatGPT

Thanks to all the contributors of the original BetterChatGPT for providing the foundation for this fork!

<a href="https://github.com/ztjhz/BetterChatGPT/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=ztjhz/BetterChatGPT" />
</a>

# 🙏 Support

If you have enjoyed using our app, we kindly ask you to give this project a ⭐️.

If you would like to support the team behind Better ChatGPT, consider sponsoring them through one of the methods below. Every contribution, no matter how small, helps us to maintain and improve their service.

| Payment Method | Link                                                                                                                                                 |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| GitHub         | [![GitHub Sponsor](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86)](https://github.com/sponsors/ztjhz) |
| KoFi           | [![support](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/betterchatgpt)                                                             |
| Alipay (Ayaka) | <img src="https://ayaka14732.github.io/sponsor/alipay.jpg" width=150 />                                                                              |
| Wechat (Ayaka) | <img src="https://ayaka14732.github.io/sponsor/wechat.png" width=150 />                                                                              |