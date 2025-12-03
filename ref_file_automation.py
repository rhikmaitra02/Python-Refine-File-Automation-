import pandas as pd
import xml.etree.ElementTree as ET
import xml.dom.minidom
import re


def generate_refine_file(input_csv, output_vrefine):

    df = pd.read_csv('Open_signals_platform_top.csv' , usecols=[0])
    signal_names = df.iloc[:, 0].dropna().unique()     #read unique lines, consider only col 0

    hierarchy = "testbench/top/SWITCHABLE_DOMAIN_PD/acp_mega_shell/"

    root = ET.Element('refinement-file-root')


    info = ET.SubElement(root, 'information', attrib={
        'comment-version': '1',
        'creator': 'auto_script',
        'csCheck': 'false',
        'save-ref-method': 'seq',
        'tool-version': 'auto'
    })
    rules = ET.SubElement(root, 'rules')

    for sig in signal_names:
        sig = str(sig).strip()
        match = re.match(r'^(.*)$(\d+)$$', sig)
        if match:
            base_name = match.group(1)
            bit_index = match.group(2)
            full_entity_name = f"{hierarchy}{base_name}/{bit_index}"
        else:
            full_entity_name = hierarchy + sig
       
           
        ET.SubElement(rules, 'rule', attrib={  #taken from format of refine file in IMC
            'ccType': 'inst',
            'comment': '0',
            'domain': 'icc',
            'entityName': full_entity_name,
            'entityType': 'toggle',
            'excTime': '0',
            'isSmart': 'true',
            'name': 'exclude',
            'reviewer': '0',
            'unexcludeFromSmart': '',
            'user': '0',
            'vscope': 'default'
     })

    xml_str = ET.tostring(root, encoding='utf-8')  
    parsed = xml.dom.minidom.parseString(xml_str)
    pretty_xml_as_str = parsed.toprettyxml(indent="  ")

    with open(output_vrefine, 'w', encoding='utf-8') as f:
        f.write(pretty_xml_as_str)


    #tree = ET.ElementTree(root)
    #tree.write('open_signals.vRefine' , encoding='utf-8', xml_declaration=True)



if __name__ == "__main__":
    generate_refine_file('Open_signals_platfrom_top.csv', 'open_signals.vRefine')