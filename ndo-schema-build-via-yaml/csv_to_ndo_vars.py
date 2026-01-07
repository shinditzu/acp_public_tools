#!/usr/bin/env python3
"""
Convert CSV files to NDO schema YAML variables
Handles nested structures like sites, subnets, and domain associations
"""

import csv
import yaml
from collections import defaultdict
from pathlib import Path


def load_csv(filepath):
    """Load CSV file and return list of dicts"""
    with open(filepath, 'r') as f:
        return list(csv.DictReader(f))


def parse_list_field(value):
    """Parse comma-separated string into list, handle empty values"""
    if not value or value.strip() == '':
        return []
    return [item.strip() for item in value.split(',')]


def parse_bool(value):
    """Parse boolean string"""
    return value.lower() in ('true', 'yes', '1')


def build_vrfs(csv_file):
    """Build VRFs from CSV"""
    rows = load_csv(csv_file)
    return [
        {
            'name': row['name'],
            'schema': row['schema'],
            'template': row['template']
        }
        for row in rows
    ]


def build_bridge_domains(bd_csv, subnet_csv=None):
    """Build bridge domains with optional subnets from separate CSV"""
    bd_rows = load_csv(bd_csv)
    
    # Build base BDs
    bds = {}
    for row in bd_rows:
        bd_name = row['name']
        bds[bd_name] = {
            'name': bd_name,
            'schema': row['schema'],
            'template': row['template'],
            'vrf': row['vrf'],
            'layer2_stretch': parse_bool(row['layer2_stretch']),
            'unicast_routing': parse_bool(row['unicast_routing']),
            'sites': []
        }
    
    # Add subnets if provided
    if subnet_csv and Path(subnet_csv).exists():
        subnet_rows = load_csv(subnet_csv)
        
        # Group subnets by BD and site
        subnets_by_bd_site = defaultdict(lambda: defaultdict(list))
        for row in subnet_rows:
            bd_name = row['bd_name']
            site_name = row['site_name']
            subnets_by_bd_site[bd_name][site_name].append({
                'ip': row['subnet_ip'],
                'scope': row['scope']
            })
        
        # Add sites and subnets to BDs
        for bd_name, sites in subnets_by_bd_site.items():
            if bd_name in bds:
                for site_name, subnets in sites.items():
                    bds[bd_name]['sites'].append({
                        'name': site_name,
                        'subnets': subnets,
                        'l3outs': None
                    })
    
    return list(bds.values())


def build_anps(csv_file):
    """Build ANPs from CSV"""
    rows = load_csv(csv_file)
    return [
        {
            'name': row['name'],
            'schema': row['schema'],
            'template': row['template']
        }
        for row in rows
    ]


def build_epgs(epg_csv, domain_csv=None):
    """Build EPGs with optional domain associations from separate CSV"""
    epg_rows = load_csv(epg_csv)
    
    # Build base EPGs
    epgs = {}
    for row in epg_rows:
        epg_name = row['name']
        epgs[epg_name] = {
            'name': epg_name,
            'schema': row['schema'],
            'template': row['template'],
            'ap': row['ap'],
            'bd': row['bd'],
            'description': row.get('description', ''),
            'vrf': row['vrf'],
            'sites': []
        }
    
    # Add domain associations if provided
    if domain_csv and Path(domain_csv).exists():
        domain_rows = load_csv(domain_csv)
        
        # Group domains by EPG and site
        domains_by_epg_site = defaultdict(lambda: defaultdict(lambda: {'phys': [], 'vmm': []}))
        for row in domain_rows:
            epg_name = row['epg_name']
            site_name = row['site_name']
            domain_type = row['domain_type']  # 'physical' or 'vmm'
            domain_name = row['domain_name']
            
            if domain_type == 'physical':
                domains_by_epg_site[epg_name][site_name]['phys'].append(domain_name)
            elif domain_type == 'vmm':
                domains_by_epg_site[epg_name][site_name]['vmm'].append(domain_name)
        
        # Add sites and domains to EPGs
        for epg_name, sites in domains_by_epg_site.items():
            if epg_name in epgs:
                for site_name, domains in sites.items():
                    epgs[epg_name]['sites'].append({
                        'name': site_name,
                        'phys_domain_association': domains['phys'],
                        'vmm_domain_association': domains['vmm']
                    })
    
    return list(epgs.values())


def main():
    """Main conversion function"""
    import argparse
    import os
    
    # Get script directory for relative paths
    script_dir = Path(__file__).parent
    
    parser = argparse.ArgumentParser(description='Convert CSV files to NDO YAML variables')
    parser.add_argument('--vrfs', default=str(script_dir / 'csv_examples/vrfs.csv'), help='VRFs CSV file')
    parser.add_argument('--bds', default=str(script_dir / 'csv_examples/bridge_domains.csv'), help='Bridge Domains CSV file')
    parser.add_argument('--subnets', default=str(script_dir / 'csv_examples/bd_subnets.csv'), help='BD Subnets CSV file (optional)')
    parser.add_argument('--anps', default=str(script_dir / 'csv_examples/anps.csv'), help='ANPs CSV file')
    parser.add_argument('--epgs', default=str(script_dir / 'csv_examples/epgs.csv'), help='EPGs CSV file')
    parser.add_argument('--domains', default=str(script_dir / 'csv_examples/epg_domains.csv'), help='EPG Domain Associations CSV file (optional)')
    parser.add_argument('--output', '-o', default=str(script_dir / 'ndo-schema-vars_fromcsv.yaml'), help='Output YAML file')
    
    args = parser.parse_args()
    
    # Build data structure
    ndo_data = {
        'ndo_schema_data': {
            'vrfs': build_vrfs(args.vrfs),
            'bridge_domains': build_bridge_domains(args.bds, args.subnets),
            'anps': build_anps(args.anps),
            'epgs': build_epgs(args.epgs, args.domains)
        }
    }
    
    # Write YAML
    with open(args.output, 'w') as f:
        f.write('# Auto-generated from CSV files\n')
        yaml.dump(ndo_data, f, default_flow_style=False, sort_keys=False)
    
    print(f"✓ Generated {args.output}")
    print(f"  - VRFs: {len(ndo_data['ndo_schema_data']['vrfs'])}")
    print(f"  - Bridge Domains: {len(ndo_data['ndo_schema_data']['bridge_domains'])}")
    print(f"  - ANPs: {len(ndo_data['ndo_schema_data']['anps'])}")
    print(f"  - EPGs: {len(ndo_data['ndo_schema_data']['epgs'])}")


if __name__ == '__main__':
    main()
