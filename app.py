import os
import json
import webbrowser
import copy
import sys
import argparse
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory, send_file

# Import PDF exporter class
from exporter import CrimpInstructionPDF

# Initialize Flask App
app = Flask(__name__, static_folder='static', static_url_path='')

# Define data directory paths relative to application root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)


def get_full_path(subfolder, filename):
    folder_path = os.path.join(DATA_DIR, subfolder)
    os.makedirs(folder_path, exist_ok=True)
    return os.path.join(folder_path, filename)


def load_json_file(subfolder, filename, default_val=None):
    if default_val is None:
        default_val = {}
    path = get_full_path(subfolder, filename)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"Error loading {path}: {e}", file=sys.stderr)
    return default_val


def save_json_file(subfolder, filename, data):
    path = get_full_path(subfolder, filename)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except (OSError, TypeError) as e:
        print(f"Error saving {path}: {e}", file=sys.stderr)
        return False


def load_settings():
    path = os.path.join(BASE_DIR, "settings.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"Error loading settings.json: {e}", file=sys.stderr)
    
    # Default settings if file does not exist or fails
    default_settings = {
        "xsec_soll_values": [
            ["0.14", 20, 20],
            ["0.25", 35, 40],
            ["0.34", 50, 65],
            ["0.50", 60, 70],
            ["0.75", 80, 90],
            ["1.00", 100, 150],
            ["1.50", 130, 210],
            ["2.50", 200, 320],
            ["4.00", 290, 500],
            ["6.00", 350, 700],
            ["10.0", 500, 950],
            ["2x1.00", 200, 300],
            ["2x1.50", 260, 420],
            ["1.00+1.50", 200, 320]
        ]
    }
    # Save default settings
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_settings, f, indent=4, ensure_ascii=False)
    except (OSError, TypeError) as e:
        print(f"Error creating default settings.json: {e}", file=sys.stderr)
    return default_settings


def save_settings(data):
    path = os.path.join(BASE_DIR, "settings.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except (OSError, TypeError) as e:
        print(f"Error saving settings.json: {e}", file=sys.stderr)
        return False


def is_safe_scheme_name(scheme):
    if not scheme:
        return False
    if "/" in scheme or "\\" in scheme or ".." in scheme:
        return False
    return all(c.isalnum() or c in ('-', '_', '.') for c in scheme)


def load_crimp_instructions():
    outdir = os.path.join(DATA_DIR, "instructions")
    instructions = {}
    if os.path.exists(outdir):
        for d in os.listdir(outdir):
            # Bugfix: Verify file ends with .json and has exactly one hyphen
            if not d.endswith(".json"):
                continue
            name_part = d[:-5]  # strip '.json'
            parts = name_part.split("-")
            if len(parts) != 2:
                continue
            schemeNr, schemeRev = parts
            if schemeNr not in instructions:
                instructions[schemeNr] = {}
            try:
                with open(os.path.join(outdir, d), "r", encoding="utf-8") as f:
                    instructions[schemeNr][schemeRev] = json.load(f)
            except (OSError, json.JSONDecodeError) as e:
                print(f"Error loading instruction file {d}: {e}", file=sys.stderr)
    return instructions


def save_crimp_instructions(scheme, full_instructions):
    outdir = os.path.join(DATA_DIR, "instructions")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, f"{scheme}.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(full_instructions, f, indent=4, ensure_ascii=False)
        return True
    except (OSError, TypeError) as e:
        print(f"Error saving instruction {scheme}: {e}", file=sys.stderr)
        return False


def delete_instruction_file(scheme):
    outdir = os.path.join(DATA_DIR, "instructions")
    filename = os.path.join(outdir, f"{scheme}.json")
    if os.path.exists(filename):
        try:
            os.remove(filename)
            return True
        except OSError as e:
            print(f"Error removing instruction file {filename}: {e}", file=sys.stderr)
    return False


def split_readable_slot(slot):
    """Convert any slot representation to [awg, met] for PDF rendering."""
    if not slot:
        return ["", ""]
    # Already a normalized [awg, met] list/tuple
    if isinstance(slot, (list, tuple)) and len(slot) >= 2:
        return [str(slot[0]), str(slot[1])]
    slot_str = str(slot)
    slot_list = slot_str.split(" | ")
    if len(slot_list) == 1:
        if "AWG" in slot_list[0]:
            return [slot_list[0].replace("AWG ", "").strip(), ""]
        if "mm²" in slot_list[0]:
            return ["", slot_list[0].replace(" mm²", "").strip()]
        return [slot_str, ""]
    if len(slot_list) >= 2:
        slot_list[0] = slot_list[0].replace("AWG ", "").strip()
        slot_list[1] = slot_list[1].replace(" mm²", "").strip()
        return slot_list[:2]
    return ["", ""]


def normalize_slot(slot):
    """Normalize any slot value to the canonical [awg, met] string-pair format."""
    if isinstance(slot, (list, tuple)) and len(slot) >= 2:
        return [str(slot[0]), str(slot[1])]
    if isinstance(slot, str):
        slot = slot.strip()
        if " | " in slot:
            parts = slot.split(" | ", 1)
            awg = parts[0].replace("AWG ", "").strip()
            met = parts[1].replace(" mm²", "").strip()
            return [awg, met]
        if slot.startswith("AWG "):
            return [slot.replace("AWG ", "").strip(), ""]
        if slot.endswith(" mm²"):
            return ["", slot.replace(" mm²", "").strip()]
        return [slot, ""]
    return ["", ""]


def build_instructions(full_instructions, crimpcontacts, crimptools):
    instructions = copy.deepcopy(full_instructions)
    to_delete = []
    for entry in full_instructions:
        parts = entry.split("#")
        if len(parts) != 2:
            to_delete.append(entry)
            continue
        xs, contactRef = parts
        
        # Safeguard fallback to prevent KeyError crashes
        if contactRef not in crimpcontacts:
            to_delete.append(entry)
            continue
            
        contact = crimpcontacts[contactRef]
        instructions[entry]["series"] = contact.get("series", "")
        instructions[entry]["producer"] = contact.get("producer", "")

        xsec_data = contact.get("crosssection", {}).get(xs)
        if not xsec_data:
            to_delete.append(entry)
            continue

        slot = xsec_data.get("slot", "")
        soll = xsec_data.get("soll", "")
        instructions[entry]["slot"] = split_readable_slot(slot)
        instructions[entry]["soll"] = soll

        tool = xsec_data.get("tool", "")
        if tool in crimptools:
            instructions[entry]["IDs"] = crimptools[tool].get("IDs", [])
            instructions[entry]["producer"] = crimptools[tool].get("producer", "")
        else:
            instructions[entry]["IDs"] = []
            instructions[entry]["producer"] = ""
            
    for entry in to_delete:
        instructions.pop(entry, None)
        
    return instructions


# --- Serve UI Frontend ---

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)


@app.route('/ewolf.png')
def serve_logo():
    return send_from_directory(BASE_DIR, 'ewolf.png')


# --- Contacts API ---

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    contacts_data = load_json_file("crimpcontacts", "crimpcontacts.json", default_val={})
    return jsonify(contacts_data)


@app.route('/api/contacts', methods=['POST'])
def save_contact():
    contact = request.json
    if not contact or "refNr" not in contact:
        return jsonify({"error": "Invalid contact data"}), 400

    # Normalize soll values to integers for consistent storage
    for xs_data in contact.get("crosssection", {}).values():
        raw_soll = xs_data.get("soll", 0)
        try:
            xs_data["soll"] = int(raw_soll)
        except (ValueError, TypeError):
            xs_data["soll"] = 0

    contacts_data = load_json_file("crimpcontacts", "crimpcontacts.json", default_val={})
    old_ref = request.args.get("oldRef", "")
    if old_ref and old_ref in contacts_data and old_ref != contact["refNr"]:
        contacts_data.pop(old_ref)

    contacts_data[contact["refNr"]] = contact
    save_json_file("crimpcontacts", "crimpcontacts.json", contacts_data)
    return jsonify({"success": True})


@app.route('/api/contacts/<ref_nr>', methods=['DELETE'])
def delete_contact(ref_nr):
    contacts_data = load_json_file("crimpcontacts", "crimpcontacts.json", default_val={})
    if ref_nr in contacts_data:
        contacts_data.pop(ref_nr)
        save_json_file("crimpcontacts", "crimpcontacts.json", contacts_data)
        return jsonify({"success": True})
    return jsonify({"error": "Contact not found"}), 404


# --- Tools API ---

@app.route('/api/tools', methods=['GET'])
def get_tools():
    tools_data = load_json_file("crimptools", "crimptools.json", default_val={})
    return jsonify(tools_data)


@app.route('/api/tools', methods=['POST'])
def save_tool():
    tool = request.json
    if not tool or "producer" not in tool or "series" not in tool or "producerNr" not in tool:
        return jsonify({"error": "Invalid tool data"}), 400

    # Normalize all slots to canonical [awg, met] string-pair format
    tool["slots"] = [normalize_slot(s) for s in tool.get("slots", [])]

    ref = f"{tool['producer']}#{tool['series']}#{tool['producerNr']}"
    tools_data = load_json_file("crimptools", "crimptools.json", default_val={})
    old_ref = request.args.get("oldRef", "")
    if old_ref and old_ref in tools_data and old_ref != ref:
        tools_data.pop(old_ref)

    tools_data[ref] = tool
    save_json_file("crimptools", "crimptools.json", tools_data)
    return jsonify({"success": True, "ref": ref})


@app.route('/api/tools/<path:tool_ref>', methods=['DELETE'])
def delete_tool(tool_ref):
    tools_data = load_json_file("crimptools", "crimptools.json", default_val={})
    if tool_ref in tools_data:
        tools_data.pop(tool_ref)
        save_json_file("crimptools", "crimptools.json", tools_data)
        return jsonify({"success": True})
    return jsonify({"error": "Tool not found"}), 404


# --- Settings API ---

@app.route('/api/settings', methods=['GET'])
def get_settings():
    return jsonify(load_settings())


@app.route('/api/settings', methods=['POST'])
def update_settings():
    settings_data = request.json
    if not settings_data or "xsec_soll_values" not in settings_data:
        return jsonify({"error": "Invalid settings data"}), 400
    save_settings(settings_data)
    return jsonify({"success": True})


# --- Instructions API ---

@app.route('/api/instructions', methods=['GET'])
def get_instructions():
    return jsonify(load_crimp_instructions())


@app.route('/api/instructions', methods=['POST'])
def save_instructions():
    data = request.json
    if not data or "scheme" not in data or "full_instructions" not in data:
        return jsonify({"error": "Invalid instructions data"}), 400
    
    scheme = data["scheme"]
    if not is_safe_scheme_name(scheme):
        return jsonify({"error": "Invalid scheme name"}), 400
        
    full_instructions = data["full_instructions"]
    override = data.get("override", False)
    
    outdir = os.path.join(DATA_DIR, "instructions")
    outfile = os.path.join(outdir, f"{scheme}.json")
    if os.path.exists(outfile) and not override:
        return jsonify({"status": "exists", "message": f'"{scheme}" ist bereits vorhanden. Überschreiben?'})
        
    save_crimp_instructions(scheme, full_instructions)
    return jsonify({"success": True})


@app.route('/api/instructions/<scheme>', methods=['DELETE'])
def delete_instructions(scheme):
    if not is_safe_scheme_name(scheme):
        return jsonify({"error": "Invalid scheme name"}), 400
    if delete_instruction_file(scheme):
        return jsonify({"success": True})
    return jsonify({"error": "File not found"}), 404


# --- PDF Generation and Export API ---

@app.route('/api/export', methods=['POST'])
def export_pdf():
    data = request.json
    if not data or "scheme" not in data or "order_details" not in data or "full_instructions" not in data:
        return jsonify({"error": "Missing parameters"}), 400
        
    scheme = data["scheme"]
    if not is_safe_scheme_name(scheme):
        return jsonify({"error": "Invalid scheme name"}), 400
    order_details = list(data["order_details"])
    full_instructions = data["full_instructions"]
    
    if len(order_details) < 4:
        order_details.append(scheme)
    
    crimpcontacts = load_json_file("crimpcontacts", "crimpcontacts.json", default_val={})
    crimptools = load_json_file("crimptools", "crimptools.json", default_val={})
    built_instr = build_instructions(full_instructions, crimpcontacts, crimptools)
    
    protocol_nr = order_details[2] if len(order_details) > 2 and order_details[2] else "unspecified"
    protocol_nr = "".join([c for c in protocol_nr if c.isalpha() or c.isdigit() or c in (' ', '_', '-')]).strip()
    
    outdir_orders = os.path.join(DATA_DIR, "orders", protocol_nr)
    os.makedirs(outdir_orders, exist_ok=True)
    
    pdf_filename = f"{scheme}.pdf"
    pdf_path = os.path.join(outdir_orders, pdf_filename)
    
    try:
        pdfcreator = CrimpInstructionPDF(outdir=outdir_orders, outfile=pdf_filename)
        pdfcreator.createPDF(order_details=order_details, instructions=built_instr)
        
        return send_file(pdf_path, mimetype='application/pdf')
        
    except (OSError, ValueError, KeyError, AttributeError, RuntimeError) as e:
        print(f"PDF creation failed: {e}", file=sys.stderr)
        return jsonify({"error": f"PDF creation failed: {str(e)}"}), 500


# --- printed orders API ---

@app.route('/api/orders', methods=['GET'])
def get_orders():
    orders_dir = os.path.join(DATA_DIR, "orders")
    if not os.path.exists(orders_dir):
        return jsonify([])
        
    orders_list = []
    for root, dirs, files in os.walk(orders_dir):
        for file in files:
            if file.lower().endswith(".pdf"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, orders_dir)
                path_parts = rel_path.split(os.sep)
                
                protocol_nr = path_parts[0] if len(path_parts) > 1 else "unspecified"
                
                stat = os.stat(full_path)
                mtime = stat.st_mtime
                size = stat.st_size
                
                orders_list.append({
                    "filename": file,
                    "protocol_nr": protocol_nr,
                    "filepath": rel_path.replace(os.sep, '/'),
                    "mtime": mtime,
                    "size": size,
                    "formatted_date": datetime.fromtimestamp(mtime).strftime("%d.%m.%Y %H:%M:%S")
                })
                
    return jsonify(orders_list)


@app.route('/api/orders/download/<path:filepath>', methods=['GET'])
def download_order_pdf(filepath):
    orders_dir = os.path.abspath(os.path.join(DATA_DIR, "orders"))
    target_path = os.path.abspath(os.path.join(orders_dir, filepath))
    
    if not target_path.startswith(orders_dir):
        return jsonify({"error": "Access denied"}), 403
        
    if not os.path.exists(target_path) or not os.path.isfile(target_path):
        return jsonify({"error": "File not found"}), 404
        
    return send_file(target_path, mimetype='application/pdf')


@app.route('/api/update', methods=['POST'])
def update_application():
    import subprocess
    import threading
    
    def perform_restart():
        print("Restarting application...", flush=True)
        os.execv(sys.executable, [sys.executable] + sys.argv)

    try:
        # Run git pull
        result = subprocess.run(["git", "pull"], capture_output=True, text=True, timeout=15)
        if result.returncode != 0:
            return jsonify({
                "success": False,
                "error": f"Git pull fehlgeschlagen (Code {result.returncode}): {result.stderr or result.stdout}"
            }), 500
        
        # Pull succeeded, schedule a restart in 1 second
        threading.Timer(1.0, perform_restart).start()
        
        return jsonify({
            "success": True,
            "message": f"Update erfolgreich. Anwendung wird neu gestartet...\n\nDetails:\n{result.stdout}"
        })
        
    except (subprocess.SubprocessError, OSError) as e:
        return jsonify({
            "success": False,
            "error": f"Update-Fehler: {str(e)}"
        }), 500


def main():
    parser = argparse.ArgumentParser(description="Start CrimpOrganizer Web Service.")
    parser.add_argument("--host", default="0.0.0.0", help="Host interface to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5050, help="Port to run server (default: 5050)")
    parser.add_argument("--no-browser", action="store_true", help="Disable launching web browser on startup")
    
    args = parser.parse_args()
    
    # Auto-open browser on local host (unless disabled or in automatic reloading worker)
    if not args.no_browser and os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        url_host = "127.0.0.1" if args.host == "0.0.0.0" else args.host
        try:
            webbrowser.open(f"http://{url_host}:{args.port}")
        except webbrowser.Error as e:
            print(f"Browser launch skipped: {e}", file=sys.stderr)
            
    app.run(host=args.host, port=args.port, debug=True)


if __name__ == '__main__':
    main()
