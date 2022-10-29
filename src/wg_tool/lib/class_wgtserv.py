"""
  wg-tool server class
"""
# pylint: disable=R0902

#from .msg import hdr_msg, warn_msg, err_msg

class WgtServer:
    """
    Our server info
    """
    # pylint: disable=R0903
    def __init__(self, serv_dict):
        self.active_users = None
        self.Address = None
        self.Hostname = None
        self.Hostname_Int = None
        self.ListenPort = None
        self.ListenPort_Int = None
        self.PrivateKey = None
        self.PublicKey = None
        self.PostUp = None
        self.PostDown = None
        self.DNS = None

        for key, val in serv_dict.items():
            setattr(self, key, val)

    def __getattr__(self,name) :
        return None

    def to_dict(self):
        """" return dict of self """
        serv_dict = vars(self)
        return serv_dict

    def endpoint(self):
        """ return endpoint for user config """
        Endpoint = f'{self.Hostname}:{self.ListenPort}'
        return Endpoint

    def endpoint_int(self):
        """ return internal endpoint for user config """
        if self.ListenPort_Int:
            Endpoint = f'{self.Hostname}:{self.ListenPort_Int}'
        else:
            Endpoint = f'{self.Hostname}:{self.ListenPort}'
        return Endpoint

    def user_allowedips(self):
        """ return default AllowedIPs for user config """
        return '0.0.0.0/0'

    def add_active_user(self, user_name):
        """ add user to active_users list (user exists check in wgtool """
        if self.active_users:
            if user_name not in self.active_users:
                self.active_users.append(user_name)
        else :
            self.active_users = [user_name]

    def remove_active_user(self, user_name):
        """ remove user from active_users list """
        changed = False
        if self.active_users:
            if user_name in self.active_users:
                self.active_users.remove(user_name)
                changed = True
        return changed

    def is_user_active(self, user_name):
        """ check if user_name is active """
        if self.active_users:
            return bool(user_name in self.active_users)
        return False
