let currentPlot = null;

document.addEventListener('DOMContentLoaded', function() {
  initializeEventListeners();
  loadCurrentParameters();
});

function initializeEventListeners() {
  document.querySelectorAll('input[data-param-name]').forEach(input => {
    input.addEventListener('change', updateParameter);
  });

  document.querySelectorAll('button[data-action]').forEach(button => {
    button.addEventListener('click', handleButtonClick);
  });
}

function loadCurrentParameters() {
  fetch('/current_params')
    .then(response => response.json())
    .then(data => {
      for (const [param, value] of Object.entries(data)) {
        const input = document.querySelector(`input[data-param-name="${param}"]`);
        if (input) {
          input.value = value;
        }
      }
    })
    .catch(error => console.error('Error loading parameters:', error));
}

function updateParameter(event) {
  const paramName = event.target.getAttribute('data-param-name');
  const value = parseFloat(event.target.value);
  
  const updateData = {};
  updateData[paramName] = value;
  
  fetch('/update_params', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(updateData)
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      updateStatus(`Parameter ${paramName} updated to ${value}`);
    } else {
      updateStatus(`Error: ${data.message}`);
    }
  })
  .catch(error => {
    console.error('Error updating parameter:', error);
    updateStatus('Error updating parameter');
  });
}

function handleButtonClick(event) {
  const action = event.target.getAttribute('data-action');
  const params = getCurrentParameters();

  switch(action) {
    case 'reset':
      resetParameters();
      break;
    case 'run_ins':
      runInsolation(params);
      break;
    case 'run_sim':
      runSimulation(params);
      break;
    case 'run_sims':
      runSimulations(params);
      break;
    case 'run_params':
      runParametersAnalysis();
      break;
    case 'plot_pars':
      runParameterPlots();
      break;
  }
}

function getCurrentParameters() {
  const params = {};
  document.querySelectorAll('input[data-param-name]').forEach(input => {
    const paramName = input.getAttribute('data-param-name');
    params[paramName] = parseFloat(input.value);
  });
  return params;
}

function resetParameters() {
  fetch('/reset')
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        loadCurrentParameters();
        updateStatus('All parameters reset to defaults');
      }
    })
    .catch(error => {
      console.error('Error resetting parameters:', error);
      updateStatus('Error resetting parameters');
    });
}

function runInsolation(params) {
  updateStatus('Generating insolation plot...');
  displayPlot('/insolation');
}

function runSimulation(params) {
  updateStatus('Generating simulation plot...');
  const sam = params.sam || 65;
  displayPlot(`/simulation?sam=${sam}`);
}

function runSimulations(params) {
  updateStatus('Generating simulations analysis...');
  const sam = params.sam || 65;
  displayPlot(`/simulations?sam=${sam}&range=_A_`);
}

function runParametersAnalysis() {
  updateStatus('Running parameter analysis...');
  displayPlot('/parameters');
}

function runParameterPlots() {
  updateStatus('Generating parameter plots...');
  displayPlot('/parameters');
}

function displayPlot(url) {
  const plotContainer = document.querySelector('.graph');
  const graphContent = document.querySelector('.graph-content');

  plotContainer.classList.add('loading');
  
  const separator = url.includes('?') ? '&' : '?';
  const timestampUrl = `${url}${separator}t=${new Date().getTime()}`;
  
  graphContent.innerHTML = `
    <div style="text-align: center;">
      <img src="${timestampUrl}" 
        alt="Plot" 
        style="max-width: 100%; border: 1px solid #333;"
        onload="hideLoader()"
        onError="hideLoader()"
    </div>
  `;
}

function hideLoader() {
  const plotContainer = document.querySelector('.graph');
  plotContainer.classList.remove('loading');
  updateStatus('Plot loaded');
}

function updateStatus(message) {
  const footer = document.querySelector('footer p');
  footer.textContent = message;
}
