import os
import re
import html

from helpscout.client import HelpScout


def get_helpscout_app_id():
    if hs_api_id := os.environ.get('HELPSCOUT_APP_ID'):
        return hs_api_id
    else:
        raise ValueError("None HELPSCOUT_APP_ID from environment variables")


def get_helpscout_app_secret():
    if hs_api_secret := os.environ.get('HELPSCOUT_APP_SECRET'):
        return hs_api_secret
    else:
        raise ValueError(
            "None HELPSCOUT_APP_SECRET from environment variables")


def is_helpdesk_url(u):
    return 'secure.helpscout.net/conversation' in u


def get_conversation_ID_from_url(hs_url):
    capture_conversation_uid = re.compile(r'.+/conversation/(\d+)/.*')

    conversation_uid_match = capture_conversation_uid.match(hs_url)

    # Handle URL that are build without the tailing /
    if conversation_uid_match is None:
        capture_conversation_uid = re.compile(r'.+/conversation/(\d+)')
        conversation_uid_match = capture_conversation_uid.match(hs_url)
    cuid = conversation_uid_match.group(1)

    if len(cuid) <= 0 or cuid is None:
        raise ValueError(
            f'Wrong help scout url {hs_url}, must have a conversation sub part with ID'
        )

    if not RepresentsInt(cuid):
        raise ValueError(f'Conversation ID : {cuid} must be an integer')

    return cuid


def get_conversation(cuid, params=None):
    app_id = get_helpscout_app_id()
    app_secret = get_helpscout_app_secret()
    hs = HelpScout(app_id, app_secret)
    if conversation := hs.conversations.get(params=params, resource_id=cuid):
        return conversation
    else:
        raise ValueError(
            "Wrong json returned from help scout, must have an item attribute")


def get_conversation_with_threads(cuid):
    return get_conversation(cuid, params='embed=threads')


def get_start_url_from_conversation(conversation_with_threads):
    embedded_conversation = conversation_with_threads._embedded
    if not embedded_conversation or not embedded_conversation["threads"][-1]:
        raise ValueError(
            "Wrong input conversation, must be not evaluate at None and have at least one thread")

    # The message to extract is the first from the thread and it was sent by a customer
    first_thread = embedded_conversation["threads"][-1]
    was_sent_by_customer = first_thread['createdBy']['type'] == 'customer'
    url_from_conversation = first_thread['body']

    if not len(url_from_conversation):
        raise ValueError("First thread from the conversation thread is empty")

    if not was_sent_by_customer:
        raise ValueError(
            "First thread from the conversation thread wasn't sent by customer")

    print(
        f'URL fetched is \033[1;36m{url_from_conversation}\033[0m sent by \033[1;33m{first_thread["customer"]["email"]}\033[0m'
    )

    return url_from_conversation


def get_emails_from_conversation(conversation_with_threads):
    embedded_conversation = conversation_with_threads._embedded
    if not conversation_with_threads or not embedded_conversation["threads"][-1]:
        raise ValueError(
            "Wrong input conversation, must be not evaluate at None and have at least one thread")

    # Extract customer
    first_thread = embedded_conversation["threads"][-1]
    customer = first_thread['customer']
    customers_mail = customer['email']
    was_sent_by_customer = first_thread['createdBy']['type'] == 'customer'

    if not was_sent_by_customer:
        raise ValueError(
            "First thread from the conversation thread wasn't sent by customer")

    emails = [customers_mail]
    if cc := first_thread['cc']:
        emails += cc

    if bcc := first_thread['bcc']:
        emails = emails + bcc

    if len(emails) > 1:
        print(
            "Conversation sent by \033[1;33m" + customers_mail + "\033[0m" + (
                " with " + " ".join(emails[1:])))

    return emails


def get_customer_id(cuid):
    app_id = get_helpscout_app_id()
    app_secret = get_helpscout_app_secret()
    hs = HelpScout(app_id, app_secret)

    for conversation in hs.hit('conversations', 'get', resource_id=cuid):
        customer_id = conversation["createdBy"]["id"]

    return customer_id


def add_draft(cuid, body):
    app_id = get_helpscout_app_id()
    app_secret = get_helpscout_app_secret()
    hs = HelpScout(app_id, app_secret)

    customer_id = get_customer_id(cuid)

    if customer_id is None:
        return False

    # Inserting HTML code into HTML mail, snippet need to be HTML escaped
    body = html.escape(body)

    data = {"text": body, "draft": True, "customer": {
        "id": customer_id
    }, }
    hs.conversations[cuid].reply.post(data=data)

    return True


def get_conversation_url_from_cuid(cuid):
    if not cuid:
        raise ValueError("Wrong input conversation ID")

    return f'https://secure.helpscout.net/conversation/{cuid}'


def check_if_is_tag(tag, ref_tag):
    '''
        Check if a tag is a ref_tag
    '''
    return tag["tag"] == ref_tag


def check_if_has_tag(conversation, ref_tags):
    '''
            Check if the conversation has one tag from ref_tags
    '''
    for ref_tag in ref_tags:
        if any(check_if_is_tag(tag, ref_tag) for tag in conversation.tags):
            return True


def is_docusaurus_conversation(conversation):
    return check_if_has_tag(conversation,
                            ["docusaurus", "ds_docusaurus",
                             "gen-docusaurus"])


def is_docusaurus_v2_conversation(conversation):
    return check_if_has_tag(conversation,
                            ["docusaurus_v2", "ds_docusaurus_v2",
                             "gen-docusaurus_v2"])


def is_gitbook_conversation(conversation):
    return check_if_has_tag(conversation, ["gitbook"])


def is_pkgdown_conversation(conversation):
    return check_if_has_tag(conversation,
                            ["pkgdown", "ds_pkgdown", "gen-pkgdown"])


def is_vuepress_conversation(conversation):
    return check_if_has_tag(conversation,
                            ["vuepress", "ds_vuepress", "gen-vuepress"])


def is_larecipe_conversation(conversation):
    return check_if_has_tag(conversation, ["larecipe"])


def is_publii_conversation(conversation):
    return check_if_has_tag(conversation,
                            ["publii", "ds_publii", "gen-publii"])


def is_jsdoc_conversation(conversation):
    return check_if_has_tag(conversation,
                            ["jsdoc", "ds_jsdoc", "gen-jsdoc"])


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
