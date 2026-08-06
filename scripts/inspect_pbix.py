import zipfile
import json
import os

def inspect_pbix():
    pbix_path = 'PowerBi/Myntra Sales Analytics.pbix'
    with zipfile.ZipFile(pbix_path, 'r') as z:
        layout_bytes = z.read('Report/Layout')
        layout = json.loads(layout_bytes.decode('utf-16le'))
        
        # Extract images saved inside PBIX
        img_dir = 'images/pbix_assets'
        os.makedirs(img_dir, exist_ok=True)
        for name in z.namelist():
            if name.startswith('Report/StaticResources/'):
                filename = os.path.basename(name)
                with open(os.path.join(img_dir, filename), 'wb') as f:
                    f.write(z.read(name))
                print(f"Extracted PBIX asset: {filename}")
                
        page = layout['sections'][0]
        print(f"\n--- Page Name: {page.get('displayName')} ---")
        print(f"Page Dimensions: {page.get('width')} x {page.get('height')}")
        
        for i, vc in enumerate(page.get('visualContainers', [])):
            config_str = vc.get('config', '{}')
            config = json.loads(config_str)
            sv = config.get('singleVisual', {})
            vtype = sv.get('visualType')
            
            title = ""
            if 'vcObjects' in sv and 'title' in sv['vcObjects']:
                t_arr = sv['vcObjects']['title']
                if t_arr and 'properties' in t_arr[0] and 'text' in t_arr[0]['properties']:
                    expr = t_arr[0]['properties']['text'].get('expr', {})
                    if 'Literal' in expr:
                        title = expr['Literal'].get('Value', '')
            
            print(f"Visual {i+1}: Type={vtype:20s} | Title='{title}' | pos=(x:{vc.get('x')}, y:{vc.get('y')}, w:{vc.get('width')}, h:{vc.get('height')})")

if __name__ == '__main__':
    inspect_pbix()
