import io
from flask import Flask, render_template, jsonify, request, send_file
from datetime import datetime
import samsim as ss
import matplotlib.pyplot as plt

app = Flask(__name__)

params = [
  {'name': 'T1', 'label': 'T1', 'type': 'number', 'value': ss._T1, 'size': '11', 'color': 'yellow'},
  {'name': 'T2', 'label': 'T2', 'type': 'number', 'value': ss._T2, 'size': '11', 'color': 'yellow'},
  {'name': 'T3', 'label': 'T3', 'type': 'number', 'value': ss._T3, 'size': '11', 'color': 'yellow'},
  {'name': 'A1', 'label': 'A1', 'type': 'number', 'value': ss._A1, 'size': '6', 'color': 'cyan'},
  {'name': 'A2', 'label': 'A2', 'type': 'number', 'value': ss._A2, 'size': '6', 'color': 'cyan'},
  {'name': 'A3', 'label': 'A3', 'type': 'number', 'value': ss._A3, 'size': '6', 'color': 'cyan'},
  {'name': 'Tm1', 'label': 'Tm1', 'type': 'number', 'value': ss._Tm1, 'size': '10', 'color': 'magenta'},
  {'name': 'Tm2', 'label': 'Tm2', 'type': 'number', 'value': ss._Tm2, 'size': '10', 'color': 'magenta'},
  {'name': 'Tm3', 'label': 'Tm3', 'type': 'number', 'value': ss._Tm3, 'size': '10', 'color': 'magenta'},
  {'name': 'Am1', 'label': 'Am1', 'type': 'number', 'value': ss._Am1, 'size': '6', 'color': 'lime'},
  {'name': 'Am2', 'label': 'Am2', 'type': 'number', 'value': ss._Am2, 'size': '6', 'color': 'lime'},
  {'name': 'Am3', 'label': 'Am3', 'type': 'number', 'value': ss._Am3, 'size': '6', 'color': 'lime'},
  {'name': 'sam', 'label': 'Samples', 'type': 'number', 'value': ss.SAM, 'size': '8', 'color': 'white'},
]

runs = [
  {'action': 'reset', 'label': 'Reset All', 'color': 'red'},
  {'action': 'run_ins', 'label': 'Insolation', 'color': 'yellow'},
  {'action': 'run_sim', 'label': 'Simulation', 'color': 'cyan'},
  {'action': 'run_sims', 'label': 'Simulations', 'color': 'magenta'},
  {'action': 'run_params', 'label': 'Parameters', 'color': 'lime'},
]

@app.route('/')
def index():
  return render_template('index.htm',
    build=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    params=params,
    runs=runs)

@app.route('/update_params', methods=['POST'])
def update_parameters():
  try:
    data = request.get_json()
    result = ss.update_params(**data)
    return jsonify({'status': 'success', 'message': result, 'current_params': ss.get_current_params()})
  except Exception as e:
    return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/reset')
def reset():
  try:
    result = ss.reset_params()
    return jsonify({'status': 'success', 'message': result, 'current_params': ss.get_current_params()})
  except Exception as e:
    return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/current_params')
def current_params():
  return jsonify(ss.get_current_params())

@app.route('/insolation')
def run_ins():
  try:
    current = ss.get_current_params()
    pars = ss.fullX(**current)
    fig = ss.plot_ins(pars)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype='image/png')
  except Exception as e:
    return jsonify({'error': str(e)}), 500

@app.route('/simulation')
def run_sim():
  try:
    sam = int(request.args.get('sam', 65))
    current = ss.get_current_params()
    pars = ss.fullX(**current)
    fig = ss.plot_sim(sam, pars)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype='image/png')
  except Exception as e:
    return jsonify({'error': str(e)}), 500

@app.route('/simulations')
def run_sims():
  try:
    sam = int(request.args.get('sam', 65))
    param_ranges = getattr(ss, request.args.get('range', '_A_'))
    fig = ss.plot_sims(sam, param_ranges)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype='image/png')
  except Exception as e:
    return jsonify({'error': str(e)}), 500

@app.route('/parameters')
def run_parameters():
  try:
    fig = ss.plot_pars()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype='image/png')
  except Exception as e:
    return jsonify({'error': str(e)}), 500

# ToDo : fix
@app.route('/animation')
def run_animation():
  try:
    param_ranges = getattr(ss, request.args.get('range', '_A_'))
    fig = ss.plot_sims(65, param_ranges)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype='image/png')
  except Exception as e:
    return jsonify({'error': str(e)}), 500

### TEST TOP ###
@app.route('/period-analysis')
def period_analysis():
  try:
    sams, fits = ss.run_params(ss._T_)
    params, _ = ss.logistic(sams, fits)
    return jsonify({
      'sams': sams.tolist(),
      'fits': fits.tolist(),
      'logistic_params': [float(p) for p in params]
    })
  except Exception as e:
    return jsonify({'error': str(e)}), 500

@app.route('/amplitude-analysis')
def amplitude_analysis():
  try:
    sams, fits = ss.run_params(ss._A_)
    params, _ = ss.logistic(sams, fits)
    return jsonify({
      'sams': sams.tolist(),
      'fits': fits.tolist(),
      'logistic_params': [float(p) for p in params]
    })
  except Exception as e:
    return jsonify({'error': str(e)}), 500

@app.route('/test-samsim')
def test_samsim():
  """Test if samsim functions work without plotting"""
  try:
    params = ss.get_current_params()
    pars = ss.fullX(**params)
    result = ss.run_ins(*pars)
    
    return jsonify({
      'status': 'success',
      'parameters': params,
      'run_ins_result_length': len(result)
    })
  except Exception as e:
    import traceback
    return jsonify({'error': str(e)}), 500
### TEST END ###

@app.route('/health')
def health_check():
  return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
