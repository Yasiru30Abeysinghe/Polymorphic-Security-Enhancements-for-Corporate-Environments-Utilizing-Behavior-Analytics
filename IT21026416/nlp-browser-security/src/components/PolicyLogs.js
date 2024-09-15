import React from 'react';

function Logs() {
  const logs = JSON.parse(localStorage.getItem('executionLogs')) || [];

  return (
    <div className="logs-container">
      <h2>Execution Logs</h2>
      {logs.length > 0 ? (
        logs.map((log, index) => (
          <div key={index} className="log-entry">
            {log.content}
          </div>
        ))
      ) : (
        <p>No policies executed yet.</p>
      )}
    </div>
  );
}

export default Logs;
