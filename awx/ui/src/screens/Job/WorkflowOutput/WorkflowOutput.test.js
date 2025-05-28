import { WorkflowJobsAPI } from 'api';
import WS from 'jest-websocket-mock';
import { act } from 'react-dom/test-utils';
import { mountWithContexts } from '../../../../testUtils/enzymeHelpers';
import WorkflowOutput from './WorkflowOutput';

jest.mock('../../../api');
jest.mock('../../../hooks/useThrottle', () => ({
  __esModule: true,
  default: jest.fn((val) => val),
}));

const job = {
  id: 1,
  name: 'Foo JT',
  status: 'successful',
};

const mockWorkflowJobNodes = [
  {
    id: 8,
    success_nodes: [10],
    failure_nodes: [],
    always_nodes: [9],
    summary_fields: {
      job: {
        elapsed: 10,
        id: 14,
        name: 'A Playbook',
        status: 'successful',
        type: 'job',
      },
    },
  },
  {
    id: 9,
    success_nodes: [],
    failure_nodes: [],
    always_nodes: [],
    summary_fields: {
      job: {
        elapsed: 10,
        id: 14,
        name: 'A Project Update',
        status: 'successful',
        type: 'project_update',
      },
    },
  },
  {
    id: 10,
    success_nodes: [],
    failure_nodes: [],
    always_nodes: [],
    summary_fields: {
      job: {
        elapsed: 10,
        id: 14,
        name: 'An Inventory Source Sync',
        status: 'successful',
        type: 'inventory_update',
      },
    },
  },
  {
    id: 11,
    success_nodes: [9],
    failure_nodes: [],
    always_nodes: [],
    summary_fields: {
      job: {
        elapsed: 10,
        id: 14,
        name: 'Pause',
        status: 'successful',
        type: 'workflow_approval',
      },
    },
  },
];

describe('WorkflowOutput', () => {
  let wrapper;
  beforeEach(() => {
    WorkflowJobsAPI.readNodes.mockResolvedValue({
      data: {
        count: mockWorkflowJobNodes.length,
        results: mockWorkflowJobNodes,
      },
    });
    window.SVGElement.prototype.height = {
      baseVal: {
        value: 100,
      },
    };
    window.SVGElement.prototype.width = {
      baseVal: {
        value: 100,
      },
    };
    window.SVGElement.prototype.getBBox = () => ({
      x: 0,
      y: 0,
      width: 500,
      height: 250,
    });

    window.SVGElement.prototype.getBoundingClientRect = () => ({
      x: 303,
      y: 252.359375,
      width: 1329,
      height: 259.640625,
      top: 252.359375,
      right: 1632,
      bottom: 512,
      left: 303,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
    delete window.SVGElement.prototype.getBBox;
    delete window.SVGElement.prototype.getBoundingClientRect;
    delete window.SVGElement.prototype.height;
    delete window.SVGElement.prototype.width;
  });

  test('renders successfully', async () => {
    await act(async () => {
      wrapper = mountWithContexts(
        <svg>
          <WorkflowOutput job={job} />
        </svg>
      );
    });
    wrapper.update();
    expect(wrapper.find('ContentError')).toHaveLength(0);
    expect(wrapper.find('WorkflowStartNode')).toHaveLength(1);
    expect(wrapper.find('WorkflowOutputNode')).toHaveLength(4);
    expect(wrapper.find('WorkflowOutputLink')).toHaveLength(5);
  });

  test('error shown to user when error thrown fetching workflow job nodes', async () => {
    WorkflowJobsAPI.readNodes.mockRejectedValue(new Error());
    await act(async () => {
      wrapper = mountWithContexts(
        <svg>
          <WorkflowOutput job={job} />
        </svg>
      );
    });
    wrapper.update();
    expect(wrapper.find('ContentError')).toHaveLength(1);
  });
  test('should establish websocket connection', async () => {
    global.document.cookie = 'csrftoken=abc123';
    const mockServer = new WS('ws://localhost/websocket/');

    await act(async () => {
      wrapper = mountWithContexts(
        <svg>
          <WorkflowOutput job={job} />
        </svg>
      );
    });
    wrapper.update();

    await mockServer.connected;
    await expect(mockServer).toReceiveMessage(
      JSON.stringify({
        xrftoken: 'abc123',
        groups: {
          jobs: ['status_changed'],
          control: ['limit_reached_1'],
        },
      })
    );
    WS.clean();
  });

  test('should refetch nodes after job status has changed', async () => {
    global.document.cookie = 'csrftoken=abc123';
    const mockServer = new WS('ws://localhost/websocket/');
    const mockReadNodes = jest.spyOn(WorkflowJobsAPI, 'readNodes');
    await act(async () => {
      wrapper = mountWithContexts(
        <svg>
          <WorkflowOutput job={job} />
        </svg>
      );
    });
    wrapper.update();

    await mockServer.connected;
    await act(async () => {
      mockServer.send(
        JSON.stringify({
          unified_job_id: 2,
          type: 'job',
          status: 'running',
        })
      );
    });
    wrapper.update();

    await act(async () => {
      await wait(500);
    });

    expect(mockReadNodes).toHaveBeenCalledTimes(1);
  });
});

function wait(milliseconds) {
  return new Promise((resolve) => {
    setTimeout(resolve, milliseconds);
  });
}
