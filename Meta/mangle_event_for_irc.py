#!/usr/bin/env python3

import json
import sys

# Must be exactly three lines each!
# No trailing newline! (I.e. keep it as backslash-newline-tripleapostrophe.)
TEMPLATE_PUSH = '''\
{commit}{post_commit} (pushed master: {status}) {compare} https://github.com/SerenityOS/serenity/actions/runs/{run_id}\
'''
TEMPLATE_PR = '''\
{title} ({actor} {action}: {status}) {link} https://github.com/SerenityOS/serenity/actions/runs/{run_id}\
'''

def compute_lines(wrapper):
    actor, run_id, raw_status, event = wrapper

    if raw_status == 'success':
        status = 'The build passed.'
    elif raw_status == 'failure':
        status = 'The build failed.'
    else:
        status = 'The build {}(?)'.format(raw_status)

    if 'action' not in event:
        # This is a push.
        if 'commits' not in event or not event['commits']:
            show_msg = '??? (No commits in event?!)'
            post_commit = ''
        else:
            commits = event['commits']
            show_commit = commits[-1]['message']
            if 'skip ci' in show_commit or 'ci skip' in show_commit:
                print('User requested to skip IRC notification. Okay!')
                return False
            # First line of the last commit:
            show_msg = show_commit.split('\n')[0]
            if len(commits) == 1:
                post_commit = ''
            elif len(commits) == 2:
                post_commit = ' (+1 commit)'
            else:
                post_commit = ' (+{} commits)'.format(len(commits))
        return TEMPLATE_PUSH.format(
            actor=actor,
            status=status,
            run_id=run_id,
            commit=show_msg,
            post_commit=post_commit,
            compare=event.get('compare', '???'),
        )
    elif 'pull_request' in event:
        # This is a PR.
        raw_action = event['action']
        if raw_action == 'opened':
            action = 'opened'
        elif raw_action == 'reopened':
            action = 'reopened'
        elif raw_action == 'synchronize':
            action = 'updated'
        else:
            action = '{}(?)'.format(raw_action)
        if event['pull_request'].get('draft', True):
            print("This is a draft PR, so IRC won't be notified.")
            print('Note: No rebuild occurs when the PR is "un-drafted"!')
            return False
        return TEMPLATE_PR.format(
            actor=actor,
            action=action,
            status=status,
            run_id=run_id,
            title=event['pull_request'].get('title', '???'),
            link=event['pull_request'].get('_links', dict()).get('html', dict()).get('href', '???'),
        )
    else:
        print('Unrecognized event type?!')
        return False


def run_on(json_string):
    wrapper = json.loads(json_string)
    line = compute_lines(wrapper)
    has_output = bool(line)
    print('::set-output name=has_output::{}'.format(has_output))
    print('> ::set-output name=has_output::{}'.format(has_output))
    if has_output:
        print('::set-output name=the_line::{}'.format(line))
        print('> ::set-output name=the_line::{}'.format(line))


def run():
    run_on(sys.stdin.read())


if __name__ == '__main__':
    run()