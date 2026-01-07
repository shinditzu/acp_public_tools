# CSV-Driven NDO Schema Configuration

## Overview
This directory contains example CSV files for driving NDO schema configuration through Ansible playbooks.

## CSV Files

### 1. **vrfs.csv**
VRF definitions
- `name`: VRF name
- `schema`: Schema name
- `template`: Template name

### 2. **bridge_domains.csv**
Bridge Domain definitions
- `name`: BD name
- `schema`: Schema name
- `template`: Template name
- `vrf`: Associated VRF name
- `layer2_stretch`: true/false
- `unicast_routing`: true/false

### 3. **bd_subnets.csv** (Optional)
BD subnet definitions per site
- `bd_name`: Bridge Domain name
- `site_name`: Site name
- `subnet_ip`: Subnet CIDR (e.g., 10.1.1.0/24)
- `scope`: Subnet scope (public/private)

### 4. **anps.csv**
Application Network Profile definitions
- `name`: ANP name
- `schema`: Schema name
- `template`: Template name

### 5. **epgs.csv**
EPG definitions
- `name`: EPG name
- `schema`: Schema name
- `template`: Template name
- `ap`: Application Profile name
- `bd`: Bridge Domain name
- `description`: EPG description
- `vrf`: VRF name

### 6. **epg_domains.csv** (Optional)
EPG domain associations per site
- `epg_name`: EPG name
- `site_name`: Site name
- `domain_type`: physical or vmm
- `domain_name`: Domain profile name

## Usage

### Convert CSV to YAML variables:
```bash
python3 csv_to_ndo_vars.py \
  --vrfs vrfs.csv \
  --bds bridge_domains.csv \
  --subnets bd_subnets.csv \
  --anps anps.csv \
  --epgs epgs.csv \
  --domains epg_domains.csv \
  --output ndo-schema-vars.yaml
```

### Run playbook with generated vars:
```bash
ansible-playbook ndo-schema-playbook.yaml
```

## Benefits of CSV Approach

1. **Easy to maintain** - Non-technical users can edit in Excel/Google Sheets
2. **Version control friendly** - Clear diffs in Git
3. **Bulk operations** - Easy to add/modify many resources at once
4. **Data validation** - Can add pre-processing validation scripts
5. **Integration** - Can pull from CMDB, IPAM, or other systems

## Alternative: Direct CSV in Playbook

For simpler use cases, you can use `read_csv` directly in your playbook:

```yaml
- name: Load configuration from CSV
  set_fact:
    ndo_schema_data:
      vrfs: "{{ lookup('ansible.builtin.read_csv', 'vrfs.csv') }}"
      bridge_domains: "{{ lookup('ansible.builtin.read_csv', 'bridge_domains.csv') }}"
```

Note: This works for flat structures but doesn't handle nested data (sites, subnets, domains).
