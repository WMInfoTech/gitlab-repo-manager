#!/usr/bin/env python3
import gitlab
import argparse
parser = argparse.ArgumentParser()

parser.add_argument("-n", "--username", help="User name")
parser.add_argument("-l", "--accesslevel", help="Access Level", type=int)
parser.add_argument("-t", "--token", help="API Token")
parser.add_argument("-p", "--project", help="Gitlab Project", type=int)
parser.add_argument('-u', '--url', help='The GitLab server name to use', required=True)

args = parser.parse_args()

gl = gitlab.Gitlab(args.url, private_token=args.token)
group = gl.groups.get(args.project)

members = group.members.list()
for member in members:
    if args.username == member.username and member.access_level >= args.accesslevel:
        print("Approved")
        exit(0)

print("You do not have the appropriate access rights!")
exit(1)
