#!/usr/bin/env python3
import argparse
import yaml
import gitlab
import sys

parser = argparse.ArgumentParser(description='Ensure that all of the expected repositories exist')
parser.add_argument('--dry-run', help='Only print what would happen', action='store_true')
parser.add_argument('-u', '--url', help='The GitLab server name to use', required=True)
parser.add_argument('-t', '--token', help='The token to use with GitLab.', required=True)
parser.add_argument('-f', '--file', help='The file to parse', required=True)
args = parser.parse_args()

# TODO: Allow the token to be pulled from an environment variable
gitlab = gitlab.Gitlab(args.url, private_token=args.token)
gitlab.auth()

existing_repo_names = list()
config = dict()

def ensure_repo_created(repo):
    group_name = config['group']['name']
    if args.dry_run:
        print('[dry run] Creating ' + group_name + '/' + repo)
    else:
        print('Create ' + group_name + '/' + repo)
        # TODO: Move this to a configuration file
        project_def = {
            'name': repo,
            'namespace_id': config['group']['id'],
            'wiki_enabled': False,
            'snippets_enabled': False,
            'container_registry_enabled': False
            # 'import_url': 'https://' # TODO: Import a project so we have a base image we like
        }
        project = gitlab.projects.create(project_def)

def get_repos_by_group(group):
    group = gitlab.groups.get(group)
    repos = list()
    for project in group.projects.list(order_by='name'):
        repos.append(project.name)

    return repos
    

if __name__ == '__main__':
    with open(args.file) as f:
        config = yaml.safe_load(f)
    
    expected_repos = config['banner_jobs']
    existing_repo_names = get_repos_by_group(config['group']['id'])

    repos_to_create = list(set(expected_repos) - set(existing_repo_names))

    for repo in repos_to_create:
        ensure_repo_created(repo)