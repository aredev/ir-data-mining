"use strict";
function newConnection() {
  return new WebSocket("ws://127.0.0.1:5678");
}

function displayStatusMsg(msg, msg_type = 'alert') {
  let oldMsgNode = document.querySelector('#status-msg');
  if (oldMsgNode) {
    oldMsgNode.remove();
  }
  
  let status_msg_node = document.createElement('div');
  status_msg_node.id = 'status-msg';
  status_msg_node.classList.add('alert', 'rounded-bottom');

  document.querySelector('#status-msg-container').appendChild(status_msg_node);
  switch (msg_type) {
    case 'alert':
      status_msg_node.classList.add('alert-info');
      break;
    case 'ok':
      status_msg_node.classList.add('alert-success');
      break;
    case 'warning':
      status_msg_node.classList.add('alert-warning');
      break;
    case 'error':
      status_msg_node.classList.add('alert-danger');
      break;
    default:
      console.error('Unknown message type: %s', msg_type);
  }
  status_msg_node.innerHTML = msg;
}

function guardConnection(ws) {
  let interval = 10;
  switch(ws.readyState) {
    case 0:
      displayStatusMsg('Connecting', 'warning');
      break;
    case 1:
      displayStatusMsg('Connected', 'ok');
      break;
    case 3:
      ws = newConnection();
      break;
    default:
      displayStatusMsg('Connection state: Unknown. Code ' + ws.readyState, 'error');
  }

  setTimeout(function () {guardConnection(ws)}, interval)
}

let ws = newConnection(),
results = document.querySelector('#result-container');
guardConnection(ws);

document.querySelector('#search-form').onsubmit = function() {
  let load_new_results = function() {
    console.log('sending query: ' + query)
    ws.send('query:' + query)
    console.log('Receiving results')
    ws.onmessage = function (event_raw) {
      let event = JSON.parse(event_raw.data);

      if (event.type === 'result') {
        let result = document.createElement('a'),
            result_html = '<h5>' + event.title + '</h5><br/><p>' + event.content + '</p>';

        result.classList.add('list-group-item', 'list-group-item-action');
        result.innerHTML = result_html;
        result.href = '#';
        results.appendChild(result);
      } else if (event.type === 'state') {
        displayStatusMsg(event.msg, 'alert')
      }
    };
  }

  results.innerHTML = '';
  let query = document.querySelector('#search-input').value;

  if (ws.readyState == 1) {
    load_new_results()
  } else {
    ws = newConnection();
    ws.onopen = load_new_results;
  }

  return false;
}
