import React from 'react';
import { act } from 'react-dom/test-utils';
import { Formik } from 'formik';
import { mountWithContexts } from '../../../../../testUtils/enzymeHelpers';
import SubscriptionStep from './SubscriptionStep';

describe('<SubscriptionStep />', () => {
  let wrapper;

  beforeAll(async () => {
    await act(async () => {
      wrapper = mountWithContexts(
        <Formik
          initialValues={{
            insights: false,
            manifest_file: null,
            manifest_filename: '',
            pendo: false,
            subscription: null,
            client_id: '',
            client_secret: '',
            redhat_password: '',
            redhat_username: '',
          }}
        >
          <SubscriptionStep />
        </Formik>
      );
    });
  });

  afterAll(() => {
    jest.clearAllMocks();
  });

  test('initially renders without crashing', async () => {
    expect(wrapper.find('SubscriptionStep').length).toBe(1);
  });

  test('should update filename when a manifest zip file is uploaded', async () => {
    expect(wrapper.find('FileUploadField')).toHaveLength(1);
    expect(wrapper.find('label').text()).toEqual(
      'Red Hat subscription manifest'
    );
    expect(wrapper.find('FileUploadField').prop('value')).toEqual(null);
    expect(wrapper.find('FileUploadField').prop('filename')).toEqual('');
    const mockFile = new Blob(['123'], { type: 'application/zip' });
    mockFile.name = 'new file name';
    mockFile.date = new Date();
    await act(async () => {
      wrapper.find('FileUpload').invoke('onChange')(mockFile, 'new file name');
    });
    await act(async () => {
      wrapper.update();
    });
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper.find('FileUploadField').prop('value')).toEqual(
      expect.stringMatching(/^[\x00-\x7F]+$/) // eslint-disable-line no-control-regex
    );
    expect(wrapper.find('FileUploadField').prop('filename')).toEqual(
      'new file name'
    );
  });

  test('clear button should clear manifest value and filename', async () => {
    await act(async () => {
      wrapper
        .find('FileUpload .pf-c-input-group button')
        .last()
        .simulate('click');
    });
    wrapper.update();
    expect(wrapper.find('FileUploadField').prop('value')).toEqual(null);
    expect(wrapper.find('FileUploadField').prop('filename')).toEqual('');
  });

  test('FileUpload should throw an error', async () => {
    expect(
      wrapper.find('div#subscription-manifest-helper.pf-m-error')
    ).toHaveLength(0);
    await act(async () => {
      wrapper.find('FileUpload').invoke('onChange')('✓', 'new file name');
    });
    wrapper.update();
    expect(
      wrapper.find('div#subscription-manifest-helper.pf-m-error')
    ).toHaveLength(1);
    expect(wrapper.find('div#subscription-manifest-helper').text()).toContain(
      'Invalid file format. Please upload a valid Red Hat Subscription Manifest.'
    );
  });

  test('Service Account / Red Hat Satellite toggle button should show credential fields', async () => {
    expect(wrapper.find('ToggleGroupItem').last().props().isSelected).toBe(
      false
    );
    wrapper
      .find(
        'ToggleGroupItem[text="Service Account / Red Hat Satellite"] button'
      )
      .simulate('click');
    wrapper.update();
    expect(wrapper.find('ToggleGroupItem').last().props().isSelected).toBe(
      true
    );
    await act(async () => {
      wrapper.find('input#client-id-field').simulate('change', {
        target: { value: 'dummyid', name: 'client_id' },
      });
      wrapper.find('input#client-secret-field').simulate('change', {
        target: { value: 'dummysecret', name: 'client_secret' },
      });
    });
    wrapper.update();
    expect(wrapper.find('input#client-id-field').prop('value')).toEqual(
      'dummyid'
    );
    expect(wrapper.find('input#client-secret-field').prop('value')).toEqual(
      'dummysecret'
    );
  });
});
