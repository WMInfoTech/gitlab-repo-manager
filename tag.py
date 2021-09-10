#!/usr/bin/env python3
import gitlab
import argparse
parser = argparse.ArgumentParser()

parser.add_argument("-t", "--token", help="API Token")
parser.add_argument("-p", "--project", help="Gitlab Project", type=int)
parser.add_argument('-u', '--url', help='The GitLab server name to use', required=True)
parser.add_argument("-v", "--tag", help="The tag name")
parser.add_argument("-b", "--branch", help="The branch name, default is main", default="main")

args = parser.parse_args()

gl = gitlab.Gitlab(args.url, private_token=args.token)
project = gl.projects.get(args.project)

try:
    protected_tag = project.protectedtags.get(args.tag)
    protected_tag.delete()
except:
    print("Tag was not protected")

try:
    project.tags.delete(args.tag)
except:
    print("Tag did not exist")

tag = project.tags.create({'tag_name': args.tag, 'ref': args.branch})

project.protectedtags.create({'name': args.tag, 'create_access_level': '40'})

exit(0)
