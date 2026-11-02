import json
from pathlib import Path
import yaml
import xmltodict
import pandas as pd
import tomli_w
try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib

def convert_data(input_path: Path, target_format: str, output_dir: Path) -> Path:
    """Convert between structured data formats (JSON, YAML, XML, TOML, CSV, TSV)."""
    src_ext = input_path.suffix.lower().lstrip(".")
    if src_ext == "yml":
        src_ext = "yaml"
        
    target_format = target_format.lower().lstrip(".")
    if target_format == "yml":
        target_format = "yaml"
        
    output_path = output_dir / f"{input_path.stem}.{target_format}"
    
    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
        
    # Parse source data
    if src_ext == "json":
        data = json.loads(content)
    elif src_ext == "yaml":
        data = yaml.safe_load(content)
    elif src_ext == "xml":
        data = xmltodict.parse(content)
    elif src_ext == "toml":
        data = tomllib.loads(content)
    elif src_ext in {"csv", "tsv"}:
        sep = "\t" if src_ext == "tsv" else ","
        df = pd.read_csv(input_path, sep=sep)
        data = df.to_dict(orient="records")
    elif src_ext in {"ini", "env"}:
        # Simple key-value parser
        data = {}
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith(("#", ";")) and "=" in line:
                k, v = line.split("=", 1)
                data[k.strip()] = v.strip()
    else:
        raise ValueError(f"Unsupported source data format: {src_ext}")

    # Serialize to target format
    if target_format == "json":
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    elif target_format == "yaml":
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)
            
    elif target_format == "toml":
        if not isinstance(data, dict):
            data = {"data": data}
        with open(output_path, "wb") as f:
            tomli_w.dump(data, f)

    elif target_format == "xml":
        if not isinstance(data, dict):
            data = {"root": {"item": data}}
        elif len(data.keys()) > 1:
            data = {"root": data}
        xml_str = xmltodict.unparse(data, pretty=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(xml_str)
            
    elif target_format in {"csv", "tsv"}:
        sep = "\t" if target_format == "tsv" else ","
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            df = pd.json_normalize(data)
        else:
            raise ValueError("Data cannot be converted to tabular format.")
        df.to_csv(output_path, sep=sep, index=False)
        
    elif target_format == "txt":
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(str(data))
    else:
        raise ValueError(f"Unsupported target data format: {target_format}")

    return output_path
