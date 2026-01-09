import pandas as pd
import re


main_csv = 'StellarX_RIF.csv'
rcc_csv = 'RCC_StellarX.csv'
output_file = 'output_sheet.arg'
cemfccu_csv = 'errtriggers.csv'
cemllp_csv = 'LLP_stellar.csv'
cemspss_csv='SPSS_stellar.csv'

#Reads header information of all three CSV files from our source cases 
main_df = pd.read_csv(main_csv, header=1)
main_df.columns = main_df.columns.str.strip()

rcc_df = pd.read_csv(rcc_csv, header=0)
rcc_df.columns = rcc_df.columns.str.strip() 
rcc_df['RIFSC'] = rcc_df['RIFSC'].str.extract(r'RIFSC_(\d+)')[0].astype('Int64')
rcc_df['Instance_num'] = rcc_df['Instance'].str.extract(r'RCC_(\d+)')[0].astype('Int64')

cemfccu_df = pd.read_csv(cemfccu_csv, header=0)
cemfccu_df.columns = cemfccu_df.columns.str.strip()

cemllp_df = pd.read_csv(cemllp_csv, header=0)
cemllp_df.columns = cemllp_df.columns.str.strip()

cemspss_df = pd.read_csv(cemspss_csv, header=0)
cemspss_df.columns = cemspss_df.columns.str.strip()



# Extraction of bus name, rifsc_id and rif index from IP Column in CEM_FCCU_PER Sheet 
def extract_bus(ip):
    m = re.search(r'(APB\d+|AHB\d+)', str(ip))
    return m.group(1) if m else None

def extract_rifsc(ip):
    m = re.search(r'RIF_RISUP_(\d+)', str(ip))
    if m:
        return int(m.group(1))
    return None

def extract_rif_index(ip):
    m = re.search(r'_(\d+)$', str(ip))
    return int(m.group(1)) if m else None

cemfccu_df['Bus'] = cemfccu_df['IP'].apply(extract_bus)
cemfccu_df['RIFSC'] = cemfccu_df['IP'].apply(extract_rifsc)
cemfccu_df['RIF index'] = cemfccu_df['IP'].apply(extract_rif_index)


# Extraction of bus name, rifsc_id and rif index from IP Column in CEM_FCCU_LLP Sheet

def extract_bus(ip):
    m = re.search(r'(APB\d+)', str(ip))
    return m.group(1) if m else None

def extract_rif_index(ip):
    m = re.search(r'_(\d+)$', str(ip))
    return int(m.group(1)) if m else None

cemllp_df['Bus'] = cemllp_df['IP'].apply(extract_bus)
cemllp_df['RIF index'] = cemllp_df['IP'].apply(extract_rif_index)



# Extraction of bus name, rifsc_id and rif index from IP Column in CEM_FCCU_SPSS Sheet 

cemspss_df['IP'] = cemspss_df['IP'].str.strip()
cemspss_df = cemspss_df[cemspss_df['IP'].str.contains(r'RIF_RISUP_(APB|AHB)\d+_\d+_\d+', na=False)]


def extract_bus_spss(ip):
    m = re.search(r'(APB\d+|AHB\d+)', str(ip))
    return m.group(1) if m else None

def extract_rifsc_spss(ip):
    # Looks for ..._BUS_<RIFSC>_RIFINDEX
    m = re.search(r'(APB\d+|AHB\d+)_([0-9]+)_\d+$', str(ip))
    return int(m.group(2)) if m else None

def extract_rif_index_spss(ip):
    m = re.search(r'_(\d+)$', str(ip))
    return int(m.group(1)) if m else None


cemspss_df['Bus'] = cemspss_df['IP'].apply(extract_bus_spss)
cemspss_df['RIFSC'] = cemspss_df['IP'].apply(extract_rifsc_spss)
cemspss_df['RIF index'] = cemspss_df['IP'].apply(extract_rif_index_spss)

print(cemspss_df[['IP', 'Bus', 'RIFSC', 'RIF index']].head(10))




##print("Columns present in CSV:", list(df.columns))

ip_col = 'IP'
rifsc_col = 'RIFSC'
rif_index_col = 'RIF index' 
bus_name = 'Bus'
bus_index = 'Bus Index'
range_byte = 'range (byte)'
dden = 'DDEN'
read_by_all = 'Read by All'
glue_n = 'Glue'
rcc_rifsc = 'RIFSC'
rcc_rel_index = 'relative index'
rcc_instance = 'Instance'
rcc_offset = 'Offset'

with open(output_file, 'w') as f:
    for idx, row in main_df.iterrows():
        ip = row[ip_col]
        rifsc = row[rifsc_col]
        rif_index = row[rif_index_col]
        if pd.isna(rifsc) or pd.isna(rif_index):
            continue  

        bus__name = row[bus_name]
        bus__index = row[bus_index]
        range_in_bytes = row[range_byte]
        dd_en = row[dden]
        glue = row[glue_n]
        read_all = row[read_by_all]
        read_by_all_num = 1 if str(read_all).strip().lower() == 'yes' else 0


        
        if idx == 0:
            f.write(f"ifeq ({ip}, $(findstring {ip}, $(test_name)))\n")
        else:
            f.write(f"else ifeq ({ip}, $(findstring {ip}, $(test_name)))\n")
        f.write(f"    C_ARG += RIFSC= {int(rifsc)}\n")
        f.write(f"    C_ARG += RIF_INDEX= {int(rif_index)}\n")
        f.write(f"    C_ARG += BUS_NAME={bus__name}\n")
        f.write(f"    C_ARG += BUS_INDEX={bus__index}\n")
        f.write(f"    C_ARG += RANGE_BYTE={range_in_bytes}\n")
        f.write(f"    C_ARG += READ_ALL={read_by_all_num}\n")

        #f.write(f"    C_ARG += DDEN={dd_en}\n")
        if dd_en == "NOAC_glue":
            f.write("    C_ARG += DDEN_NOAC_glue=1\n")
        elif dd_en == "HDE_glue":
            f.write("    C_ARG += DDEN_HDE_glue=1\n")
        elif dd_en == "DDEN_glue":
            f.write("    C_ARG += DDEN_DDEN_glue=1\n")
        elif dd_en == "tied to 1":
            f.write("    C_ARG += DDEN_tied_to_1=1\n")


        if glue == "OR2_SERF":
            f.write("    C_ARG += GLUE_SERF=1\n")
        elif glue == "OR2_DDEN":
            f.write("    C_ARG += GLUE_DDEN=1\n")
        elif glue == "OR3_DDEN_SERF":
            f.write("    C_ARG += GLUE_DDEN_SERF=1\n")

        for rcc_num in [0,1,2]:
            matches = rcc_df[
                    (rcc_df[rcc_rifsc] == rifsc) &
                    (rcc_df[rcc_rel_index] == rif_index) &
                    (rcc_df['Instance_num'] == rcc_num)
                    ]
            if not matches.empty:
                f.write(f"    C_ARG += RCC_{rcc_num}=1\n")

        for _, rcc_row in matches.iterrows():
                offset_rcc  = matches.iloc[0][rcc_offset]
                f.write(f"    C_ARG += RCC_OFFSET={offset_rcc}\n")
        
        #CEM FIle matching for each of the 3 tabs of CEM_FCCU sheet 

        cem_matches1 = cemfccu_df[
            (cemfccu_df['RIFSC'] == rifsc) &
            (cemfccu_df['RIF index'] == rif_index) &
            (cemfccu_df['Bus'] == bus__name)
        ]
        if not cem_matches1.empty:
            for _, cem_row in cem_matches1.iterrows():
                fccu_channel = int(cem_row['FCCU channel'])
                #cem = int(cem_row['CEM'])
                cem_values = cem_matches1['CEM'].dropna().astype(int).unique()
                or_group = int(cem_row['OR-Group'])
                bit = int(cem_row['Bit'])
                f.write(f"    C_ARG += FCCU_CHANNEL={fccu_channel}\n")
                f.write(f"    C_ARG += OR_GROUP={or_group}\n")
                f.write(f"    C_ARG += BIT={bit}\n")
                for cem_num in cem_values:
                    f.write(f"    C_ARG += CEM_{cem_num} = 1\n")

        
        cem_matches2 = cemllp_df[
            (cemllp_df['RIF index'] == rif_index) &
            (cemllp_df['Bus'] == bus__name)
        ]
        if not cem_matches2.empty:
            for _, cem_row in cem_matches2.iterrows():
                fccu_channel = int(cem_row['FCCU channel'])
                cem = int(cem_row['CEM'])
                cem_values = cem_matches2['CEM'].dropna().astype(int).unique()
                or_group = int(cem_row['OR-Group'])
                bit = int(cem_row['Bit'])
                f.write(f"    C_ARG += FCCU_CHANNEL={fccu_channel}\n")
                f.write(f"    C_ARG += OR_GROUP={or_group}\n")
                f.write(f"    C_ARG += BIT={bit}\n")
                for cem_num in cem_values:
                    f.write(f"    C_ARG += CEM_{cem_num} = 1\n")
    
        

        spss_matches3 = cemspss_df[
            (cemspss_df['RIF index'] == rif_index) &
            (cemspss_df['Bus'] == bus__name)
                ]
        if not spss_matches3.empty:
            for _, spss_row in spss_matches3.iterrows():
                fccu_channel = int(spss_row['FCCU channel'])
                cem_values = spss_row['CEM']
                or_group = int(spss_row['OR-Group'])
                bit = int(spss_row['Bit'])
                f.write(f"    C_ARG += FCCU_CHANNEL={fccu_channel}\n")
                cem_values_upper = [str(val).strip().upper() for val in cem_values]
                if "S" in cem_values_upper or "P" in cem_values_upper:
                    f.write(f"    C_ARG += CEM_SP=1\n")
                else:
                    for cem_val in cem_values_upper:
                         f.write(f"    C_ARG += CEM_{cem_val}=1\n")
                
                f.write(f"    C_ARG += OR_GROUP={or_group}\n")
                f.write(f"    C_ARG += BIT={bit}\n")

    f.write("endif\n")
        

print(f"ARG file generated: {output_file}")
