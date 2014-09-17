from pixelated.adapter.pixelated_mailbox import PixelatedMailbox


class PixelatedMailBoxes():

    def __init__(self, account):
        self.account = account

    def _create_or_get(self, mailbox_name):
        mailbox_name = mailbox_name.upper()
        if mailbox_name not in self.account.mailboxes:
            self.account.addMailbox(mailbox_name)
        return PixelatedMailbox.create(self.account, mailbox_name)

    def drafts(self):
        return self._create_or_get('DRAFTS')

    def trash(self):
        return self._create_or_get('TRASH')

    @property
    def mailboxes(self):
        return [PixelatedMailbox.create(self.account, leap_mailbox_name) for leap_mailbox_name in
                self.account.mailboxes]

    def mails_by_tag(self, query_tags):
        mails = []
        for mailbox in self.mailboxes:
            mails.extend(mailbox.mails_by_tags(query_tags))

        return mails

    def add_draft(self, mail):
        drafts = self.drafts()
        draft_id = drafts.add(mail)
        mail.set_ident(drafts.mailbox_name, draft_id)
        return mail

    def move_to_trash(self, mail):
        mail.remove_all_tags()
        origin_mailbox = mail.mailbox_name

        self._create_or_get(origin_mailbox).remove(mail)
        return self.trash().add(mail)

    def mail(self, mail_id):
        for mailbox in self.mailboxes:
            mail = mailbox.mail(mail_id)
            if mail:
                return mail
