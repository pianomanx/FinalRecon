#!/usr/bin/env python3

import dnslib
from modules.export import export

R = '\033[31m'  # red
G = '\033[32m'  # green
C = '\033[36m'  # cyan
W = '\033[0m'   # white
Y = '\033[33m'  # yellow


def dnsrec(domain, output, data):
	result = {}
	print(f'\n{Y}[!] Starting DNS Enumeration...{W}\n')
	dns_records = ['A', 'AAAA', 'ANY', 'CAA', 'CNAME', 'MX', 'NS', 'TXT']
	full_ans = []
	for dns_record in dns_records:
		q = dnslib.DNSRecord.question(domain, dns_record)
		pkt = q.send('8.8.8.8', 53, tcp='UDP')
		ans = dnslib.DNSRecord.parse(pkt)
		ans = str(ans)
		ans = ans.split('\n')
		full_ans.extend(ans)
	full_ans = set(full_ans)
	dns_found = []

	for entry in full_ans:
		if not entry.startswith(';'):
			dns_found.append(entry)

	if not dns_found:
		print(f'{R}[-] {C}DNS Records Not Found!{W}')
		if output != 'None':
			result.setdefault('dns', ['DNS Records Not Found'])
	else:
		for entry in dns_found:
			print(f'{C}{entry}{W}')
			if output != 'None':
				result.setdefault('dns', []).append(entry)

	dmarc_target = f'_dmarc.{domain}'
	q = dnslib.DNSRecord.question(dmarc_target, 'TXT')
	pkt = q.send('8.8.8.8', 53, tcp='UDP')
	dmarc_ans = dnslib.DNSRecord.parse(pkt)
	dmarc_ans = str(dmarc_ans)
	dmarc_ans = dmarc_ans.split('\n')
	dmarc_found = []

	for entry in dmarc_ans:
		if entry.startswith('_dmarc') is True:
			dmarc_found.append(entry)

	if not dmarc_found:
		print(f'\n{R}[-] {C}DMARC Record Not Found!{W}')
		if output != 'None':
			result.setdefault('dmarc', ['DMARC Record Not Found!'])
	else:
		for entry in dmarc_found:
			print(f'{C}{entry}{W}')
			if output != 'None':
				result.setdefault('dmarc', []).append(entry)
	result.update({'exported': False})

	if output != 'None':
		data['module-DNS Enumeration'] = result
		fname = f'{output["directory"]}/dns_records.{output["format"]}'
		output['file'] = fname
		export(output, data)
