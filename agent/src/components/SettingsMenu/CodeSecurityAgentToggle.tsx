import { useTranslation } from 'react-i18next';
import useStore from '@store/store';
import React, { useEffect, useState } from 'react';
import Toggle from '@components/Toggle';


export const CodeSecurityAgentToggle = () => {
  const { t } = useTranslation('main');

  const setSecurityAgent = useStore((state) => state.setCodeSecurityAgent);

  const [isChecked, setIsChecked] = useState<boolean>(
    useStore.getState().codeSecurityAgent
  );

  useEffect(() => {
    setSecurityAgent(isChecked);
  }, [isChecked]);

  return (
    <Toggle
      label={t('codeSecurityAgent') as string}
      isChecked={isChecked}
      setIsChecked={setIsChecked}
    />
  );
};