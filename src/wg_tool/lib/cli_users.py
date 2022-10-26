"""
   Helpers for parse the list of user:prof,prof, ..

     - cli_user_prof_names()
       dictionary of users and profiles from command line.

     - all_users_prof_names()
       dictionary of all users and all profiles
"""

def _split_cli_user_profiles(user_name_prof):
    """
    Split one of command line elements of one user and profiles:
        user_name_prof = 'user_name:prof1,prof2,...
      into:
        (user_name, ['prof1', 'prof2', ...])
    if no profiles then array is empty []
    """
    prof_names = []
    pass1 = user_name_prof.partition(':')
    user_name = pass1[0]
    prof_list = pass1[2]
    if prof_list:
        prof_names = prof_list.split(',')
    return (user_name, prof_names)

def cli_user_prof_names(wgtool):
    """
    function to parse command line users/profiles
    From command line users/profiles
      - returns dictionary:
        { 'user1' : [prof1, prof2, ...],
          'user2' : [prof1, ...]
    - if no users then {}. if user and no profiles then {'user' : [] }
    """
    users_profiles = {}
    if wgtool.opts.users :
        for user_prof_names in wgtool.opts.users:
            (user_name, prof_names) = _split_cli_user_profiles(user_prof_names)
            users_profiles[user_name] = prof_names

    return users_profiles

def all_users_prof_names(wgtool):
    """
    Make dictionary of all  users and their profiles :
    """
    users_profiles = {}
    for user_name in wgtool.users_all:
        user = wgtool.users[user_name]
        users_profiles[user_name] = user.profile_names()
    return users_profiles
