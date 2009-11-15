#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Check the prerequisites for iPhone development
#

import os, sys, subprocess, re, types
import poorjson, run

template_dir = os.path.abspath(os.path.dirname(sys._getframe(0).f_code.co_filename))

def sdk_found(apiversion):
	if not os.path.exists('/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS%s.sdk' % apiversion):
		return False
	if not os.path.exists('/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator%s.sdk' % apiversion):
		return False
	return True


def get_sdks():
	found = []
	output = run.run(["xcodebuild","-showsdks"])
	for line in output.split("\n"):
		if line[0:1] == '\t':
			line = line.strip()
			i = line.index('-sdk')
			type = line[0:i]
			cmd = line[i+5:]
			m = re.findall(r"iphoneos3\.1$",cmd)
			if len(m) > 0 and sdk_found('3.1'):
				found.append('3.1')

			m = re.findall(r"iphoneos3\.0$",cmd)
			if len(m) > 0 and sdk_found('3.0'):
				found.append('3.0')
			
			m = re.findall(r"iphoneos2\.2\.1$",cmd)
			if len(m) > 0 and sdk_found('2.2.1'):
				found.append('2.2.1')
	return found
	
def check_iphone3():
	try:
		found = get_sdks()		
		if len(found) > 0:
			sys.stdout.write('{"success":true, "sdks":[')
			c = 0
			for name in found:
				sys.stdout.write(('"%s"' % name))
				if c+1 < len(found):
					sys.stdout.write(",")
				c+=1
			sys.stdout.write(']}')
			print
			sys.exit(0)
		else:				
			print '{"success":false,"message":"Missing iPhone SDK which supports either 2.2.1 or 3.0"}'
			sys.exit(2)

		
	except Exception, e:
		print '{"success":false,"message":"Missing Apple XCode"}'
		sys.exit(1)

def check_itunes_version(props):
	ver = run.run(['osascript',os.path.join(template_dir,'itunes_ver.scpt')]).strip()
	props['itunes_version']=ver
	props['itunes']=False
	props['itunes_message']=None
	if ver:
		major = int(ver[0])
		minor = int(ver[2])
		if (major == 8 and minor >= 2) or major > 8:
			props['itunes']=True
			return
	props['itunes_message'] = 'iTunes 8.2 or later required. You have %s' % ver		

def check_for_wwdr(props,line):
	if len(re.findall('Apple Worldwide Developer Relations Certification Authority',line)) > 0:
		props['wwdr']=True
		props['wwdr_message']=None
	
def check_for_iphone_dev(props,line):
	m = re.search(r'\"iPhone Developer: (.*)\"',line)
	if not m == None:
		name = m.group(1).strip()
		props['iphone_dev']=True
		if props.has_key('iphone_dev_name'):
			try:
				props['iphone_dev_name'].index(name)
			except:
				props['iphone_dev_name'].append(name)
		else:
			props['iphone_dev_name']=[name]
		props['iphone_dev_message']=None

def check_for_iphone_dist(props,line):
	m = re.search(r'\"iPhone Distribution: (.*)\"',line)
	if not m == None:
		name = m.group(1).strip()
		props['iphone_dist']=True
		if props.has_key('iphone_dist_name'):
			try:
				props['iphone_dist_name'].index(name)
			except:
				props['iphone_dist_name'].append(name)
		else:
			props['iphone_dist_name']=[name]
		props['iphone_dist_message']=None
	
def check_certs(props):
	props['wwdr']=False
	props['wwdr_message'] = "Missing the Apple WWDR intermediate certificate."
	props['iphone_dist']=False
	props['iphone_dev']=False
	props['iphone_dist_message'] = 'Missing iPhone Distribution Certificate'
	props['iphone_dev_message'] = 'Missing iPhone Developer Certificate'
	output = run.run(['security','dump-keychain']).decode("utf-8")
	for i in output.split('\n'):
		check_for_wwdr(props,i)
		check_for_iphone_dev(props,i)
		check_for_iphone_dist(props,i)

	
def check_for_package():
	props = {}
	check_itunes_version(props)
	check_certs(props)
	props['sdks']=get_sdks()
	print poorjson.PoorJSON().dump(props)
			
def main(args):
	if len(args)!=2:
		print "Usage: %s <project|package>" % os.path.basename(args[0])
		sys.exit(1)

	if args[1] == 'project':
		check_iphone3()
	else:
		check_for_package()	
		
	sys.exit(0)

if __name__ == "__main__":
    main(sys.argv)

