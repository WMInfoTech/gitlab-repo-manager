#!/usr/bin/env python3
import argparse
import yaml
import gitlab
import sys
import pygit2
import shutil
import os

parser = argparse.ArgumentParser(description='Ensure that all of the expected repositories exist')
parser.add_argument('--dry-run', help='Only print what would happen', action='store_true')
parser.add_argument('-u', '--url', help='The GitLab server name to use', required=True)
parser.add_argument('-t', '--token', help='The token to use with GitLab.', required=True)
parser.add_argument('-i', '--user', help='Username/Identity to push/pull templates (should match the token)', required=True)
parser.add_argument('-f', '--file', help='The file to parse', required=True)
args = parser.parse_args()

# TODO: Allow the token to be pulled from an environment variable
gitlab = gitlab.Gitlab(args.url, private_token=args.token)
gitlab.auth()

# Setup credentials for pushing/pulling
gitlab_creds = pygit2.UserPass(args.user, args.token)
pygit_callback = pygit2.RemoteCallbacks(credentials=gitlab_creds)

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
        }
        project = gitlab.projects.create(project_def)

def get_repos_by_group(group):
    print('Pulling a list of repositories')
    group = gitlab.groups.get(group)
    repos = list()
    for project in group.projects.list(order_by='name', all=True):
        repos.append(project.name)
    repos.sort()
    return repos

def get_templates(templates):
    os.mkdir('templates')
    for name in templates.keys():
        print("Cloning " + templates[name])
        pygit2.clone_repository(templates[name], 'templates/'+name, callbacks=pygit_callback)

def populate_repo(repo_name, template):
    # Populate the repository
    shutil.copytree('templates/' + template, 'temp', ignore=shutil.ignore_patterns('.git'))
    repo = pygit2.init_repository('temp', bare=False)

    # Create a commit
    index = repo.index
    index.add_all()
    index.write()
    tree = index.write_tree()

    author = pygit2.Signature('Repo Manager', 'eis_deploy_user@lists.wm.edu')
    message = "Initial Commit"

    oid = repo.create_commit('refs/heads/master', author, author, message, tree, [])

    # Create a remote and push
    remote_url = args.url + '/' + config['group']['name'] + '/' + repo_name
    repo.remotes.create('origin', remote_url)
    if args.dry_run:
        print('[dry run] Pushing template')
    else:
        repo.remotes['origin'].push(['refs/heads/master'], callbacks=pygit_callback)

    # Cleanup from where we populated the repo
    # os.rmdir('temp')


if __name__ == '__main__':
    with open(args.file) as f:
        config = yaml.safe_load(f)
    
    expected_repos = config['repositories']
    expected_repos.sort()

    existing_repo_names = get_repos_by_group(config['group']['id'])
    repos_to_create = list(set(expected_repos) - set(existing_repo_names))

    if len(repos_to_create) > 0:
        print("Repositories to create - cloning templates")
        get_templates(config['templates'])

    for repo in repos_to_create:
        ensure_repo_created(repo)
        populate_repo(repo, 'default')