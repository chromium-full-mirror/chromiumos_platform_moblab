/*
* Copyright 2018 The Chromium OS Authors. All rights reserved.
* Distributed under the terms of the GNU General Public License v2.
*/
const http = require('http');
const url = require('url');
const port = 3000;

const api = {
  '/GetStatus': () => {
    return [
      {
        healthchecks: [],
        health: true,
        service: 'healthyService'
      },
      {
        healthchecks: [
          {
            health: true,
            name: 'warningCheck',
            actions: [],
            description: 'a check that produced warnings'
          }
        ],
        health: true,
        service: 'warningService'
      },
      {
        healthchecks: [
          {
            health: false,
            name: 'errorCheck',
            actions: ['testAction', 'testActionWithParams'],
            description: 'a check that produced errors'
          }
        ],
        health: false,
        service: 'unhealthyService'
      }
    ];
  },
  '/ActionInfo': (query) => {
    if(query.action === 'testActionWithParams'){
      return {
        action: 'testActionWithParams',
        info: 'some info about this action',
        params: {testParam: 'info about this param'}
      };
    }
    else {
      return {
        action: 'testAction',
        info: 'some info about this action',
        params: {}
      };
    }
  },
  '/RepairService': () => {
    return {};
  },
  '/CollectLogs': () => {
    return 'this is a log';
  },
  '/ListDiagnosticChecks': () => {
    return [{
      category: 'test category 1',
      checks: [{
        name: 'test check 1',
        description: 'a diagnostic test'
      },
      {
        name: 'test check 2',
        description: 'a second diagnostic test'
      }]
    },
    {
      category: 'test category 2',
      checks: [{
        name: 'test check 2',
        description: 'another diagnostic test'
      }]
    }];
  },
  '/RunDiagnosticCheck': (query) => {
    return {
      result: `you have run a diagnostic, congratulations`
    };
  }
}

const requestHandler = (request, response) => {
  response.setHeader('Content-Type', 'application/json');
  const parsed = url.parse(request.url, true);
  const handler = api[parsed.pathname] || function(){return ''};
  const data = handler(parsed.query);
  response.end(JSON.stringify(data));
}

const server = http.createServer(requestHandler)

server.listen(port, (err) => {
  console.log(`mock api server is listening on ${port}`)
})
