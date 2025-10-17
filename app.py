import io
from flask import Flask, render_template, jsonify, request, send_file
from datetime import datetime
import samsim as ss
import matplotlib.pyplot as plt

app = Flask(__name__)

params = [
  [{'name': name, 'label': name, 'type': 'number', 'value': val, 'size': size, 'color': color}
  for name, val, size in params_list]
  for color, params_list in [
    ('red', [('T1', ss._T1, 11), ('A1', ss._A1, 6), ('Tm1', ss._Tm1, 10), ('Am1', ss._Am1, 6)]),
    ('green', [('T2', ss._T2, 11), ('A2', ss._A2, 6), ('Tm2', ss._Tm2, 10), ('Am2', ss._Am2, 6)]),
    ('yellow', [('T3', ss._T3, 11), ('A3', ss._A3, 6), ('Tm3', ss._Tm3, 10), ('Am3', ss._Am3, 6)]),
    ('white', [('sam', ss.SAM, 8)])
  ]
]

runs = [
  {'action': 'reset', 'label': 'Reset All', 'color': 'red'},
  {'action': 'run_ins', 'label': 'Insolation', 'color': 'yellow'},
  {'action': 'run_sim', 'label': 'Simulation', 'color': 'cyan'},
  {'action': 'run_sims', 'label': 'Simulations', 'color': 'magenta'},
  {'action': 'run_params', 'label': 'Parameters', 'color': 'lime'},
]

flat_params = [param for group in params for param in group]

@app.route('/')
def index():
  return render_template('index.htm',
    build=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    params=flat_params,  # Use flat_params instead of grouped
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

@app.route('/health')
def health_check():
  return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
