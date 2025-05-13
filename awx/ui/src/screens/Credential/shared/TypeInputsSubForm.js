import React from 'react';

import { t, Trans } from '@lingui/macro';
import { Alert, FormGroup, Title } from '@patternfly/react-core';
import {
  FormCheckboxLayout,
  FormColumnLayout,
  FormFullWidthLayout,
  SubFormLayout,
} from 'components/FormLayout';
import { CheckboxField } from 'components/FormField';
import { CredentialType } from 'types';
import { CredentialField, GceFileUploadField } from './CredentialFormFields';

function TypeInputsSubForm({ credentialType }) {
  const stringFields = credentialType.inputs.fields.filter(
    (fieldOptions) => fieldOptions.type === 'string' || fieldOptions.choices
  );
  const booleanFields = credentialType.inputs.fields.filter(
    (fieldOptions) => fieldOptions.type === 'boolean'
  );
  return (
    <SubFormLayout>
      <Title size="md" headingLevel="h4">
        {t`Type Details`}
      </Title>
      <FormColumnLayout>
        {credentialType?.kind === 'insights' && (
          <FormFullWidthLayout>
            <Alert
              variant="info"
              isInline
              title={t`Input username and password or client ID and client secret.`}
            >
              <Trans>
                Enter your client ID and client secret to create your Insights
                credential. See this{' '}
                <a
                  href="https://access.redhat.com/articles/7108804"
                  target="_blank"
                  rel="noreferrer"
                >
                  <strong>Knowledgebase article</strong>
                </a>{' '}
                for more detail.
              </Trans>
            </Alert>
          </FormFullWidthLayout>
        )}
        {credentialType.namespace === 'gce' && <GceFileUploadField />}
        {stringFields.map((fieldOptions) =>
          fieldOptions.multiline ? (
            <FormFullWidthLayout key={fieldOptions.id}>
              <CredentialField
                credentialType={credentialType}
                fieldOptions={fieldOptions}
              />
            </FormFullWidthLayout>
          ) : (
            <CredentialField
              key={fieldOptions.id}
              credentialType={credentialType}
              fieldOptions={fieldOptions}
            />
          )
        )}
        {booleanFields.length > 0 && (
          <FormFullWidthLayout>
            <FormGroup fieldId="credential-checkboxes" label={t`Options`}>
              <FormCheckboxLayout>
                {booleanFields.map((fieldOptions) => (
                  <CheckboxField
                    id={`credential-${fieldOptions.id}`}
                    key={fieldOptions.id}
                    name={`inputs.${fieldOptions.id}`}
                    label={fieldOptions.label}
                    tooltip={fieldOptions.help_text}
                  />
                ))}
              </FormCheckboxLayout>
            </FormGroup>
          </FormFullWidthLayout>
        )}
      </FormColumnLayout>
    </SubFormLayout>
  );
}

TypeInputsSubForm.propTypes = {
  credentialType: CredentialType.isRequired,
};

TypeInputsSubForm.defaultProps = {};

export default TypeInputsSubForm;
