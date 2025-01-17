#!/usr/bin/env python3
"""
Checkmk Rules
"""
#pylint: disable=import-error
from application.modules.rule.rule import Rule
from application.modules.debug import debug as print_debug
from application.modules.debug import ColorCodes
from application.modules.checkmk import poolfolder

class CheckmkRulesetRule(Rule): # pylint: disable=too-few-public-methods, too-many-locals, too-many-nested-blocks
    """
    Rule to create Rulesets in Checkmk
    """

    name = "Checkmk -> CMK Rules Managment"


    def add_outcomes(self, rule, outcomes):
        """
        Add matching Rules to the set
        """
        for outcome in rule:
            ruleset_type = outcome['ruleset']
            outcomes.setdefault(ruleset_type, [])
            outcomes[ruleset_type].append(outcome)
        return outcomes


class DefaultRule(Rule):
    """
    Just adds all to the set
    """
    def add_outcomes(self, rule, outcomes):
        """
        Add matching Rules to the set
        """
        outcomes.setdefault('default', [])
        for outcome in rule:
            outcomes['default'].append(outcome)
        return outcomes

class CheckmkRule(Rule): # pylint: disable=too-few-public-methods
    """
    Class to get actions for rule
    """

    name = "Checkmk -> Export Rules"

    found_poolfolder_rule = False # Spcific Helper for this kind of action
    db_host = False

    @staticmethod
    def format_foldername(folder):
        """ Format Foldername """
        if not folder.startswith('/'):
            folder = "/" + folder
        if folder.endswith('/'):
            folder = folder[:-1]
        return folder.lower()


    def add_outcomes(self, rule, outcomes):
        """ Handle the Outcomes """
        #pylint: disable=too-many-branches, too-many-statements

        for outcome in rule:
            # We add only the outcome of the
            # first matching rule action
            # exception are the folders

            # Prepare empty string to add later on subfolder if needed
            # We delete it anyway at the end, if it's stays empty

            outcomes.setdefault('move_folder',"")
            outcomes.setdefault('attributes', [])
            outcomes.setdefault('custom_attributes', [])
            outcomes.setdefault('remove_attributes', [])
            outcomes.setdefault('create_cluster', [])

            if outcome['action'] == 'move_folder':
                outcomes['move_folder'] += self.format_foldername(outcome['action_param'])

            if outcome['action'] == 'folder_pool':
                self.found_poolfolder_rule = True
                if self.db_host.get_folder():
                    outcomes['move_folder'] += self.db_host.get_folder()
                else:
                    # Find new Pool Folder
                    only_pools = None
                    if outcome['action_param']:
                        only_pools = [x.strip() for x in outcome['action_param'].split(',')]
                    folder = poolfolder.get_folder(only_pools)
                    if not folder:
                        raise Exception(f"No Pool Folder left for {self.db_host.hostname}")
                    folder = self.format_foldername(folder)
                    self.db_host.lock_to_folder(folder)
                    outcomes['move_folder'] += folder

            if outcome['action'] == 'attribute':
                outcomes['attributes'].append(outcome['action_param'])

            if outcome['action'] == 'custom_attribute':
                new_key, new_value = outcome['action_param'].split(':')
                hostname = self.db_host.hostname
                new_value = new_value.replace('{{hostname}}', hostname)
                if new_value.lower() in ['none', 'false']:
                    outcomes['remove_attributes'].append(new_key)
                else:
                    outcomes['custom_attributes'].append({new_key: new_value})

            print_debug(self.debug,
                        "- Handle Special options")

            if outcome['action'] == 'value_as_folder':
                search_tag = outcome['action_param']
                print_debug(self.debug,
                            f"---- value_as_folder matched, search tag '{search_tag}'")
                for tag, value in self.attributes.items():
                    if search_tag == tag:
                        if value and value != 'null':
                            print_debug(self.debug, f"----- {ColorCodes.OKGREEN}Found tag"\
                                                    f"{ColorCodes.ENDC}, add folder: '{value}'")
                            outcomes['move_folder'] += self.format_foldername(value)
                        else:
                            print_debug(self.debug, \
                                f"----- {ColorCodes.OKGREEN}Found tag but content null")

            if outcome['action'] == 'tag_as_folder':
                search_value = outcome['action_param']
                print_debug(self.debug,
                            f"---- tag_as_folder matched, search value '{search_value}'")
                for tag, value in self.attributes.items():
                    if search_value == value:
                        if value and value != 'null':
                            print_debug(self.debug, f"------ {ColorCodes.OKGREEN}Found value"\
                                                    f"{ColorCodes.ENDC}, add folder: '{tag}'")
                            outcomes['move_folder'] += self.format_foldername(tag)
                        else:
                            print_debug(self.debug, \
                                f"----- {ColorCodes.OKGREEN}Found value but content null")

            if outcome['action'] == 'create_cluster':
                params = [x.strip() for x in outcome['action_param'].split(',')]
                for node_tag in params:
                    if node_tag.endswith('*'):
                        for tag, value in self.attributes.items():
                            if tag.startswith(node_tag[:-1]):
                                outcomes['create_cluster'].append(value)
                    else:
                        if node := self.attributes.get(node_tag):
                            outcomes['create_cluster'].append(node)

            # Cleanup in case not folder rule applies,
            # we have nothing to return to the plugins
            if not outcomes['move_folder']:
                del outcomes['move_folder']
            if not outcomes['remove_attributes']:
                del outcomes['remove_attributes']

        print_debug(self.debug, "")
        return outcomes



    def check_rule_match(self, db_host):
        """
        Overwritten cause of folder_pool
        """

        hostname = db_host.hostname
        #pylint: disable=too-many-branches

        self.found_poolfolder_rule = False
        self.db_host = db_host
        outcomes = self.check_rules(hostname)
        # Cleanup Pool folder since no match
        # to a poolfolder rule anymore
        if not self.found_poolfolder_rule:
            if db_host.get_folder():
                old_folder = db_host.get_folder()
                db_host.lock_to_folder(False)
                poolfolder.remove_seat(old_folder)
        return outcomes
