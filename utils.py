import asyncio
import json
from datetime import datetime, date
from enum import member
from math import nextafter

import discord
import nextcord
import paramiko
import logging

from nextcord import DMChannel, Client, Member, Guild, Message, Role
from nextcord.abc import GuildChannel
from python_freeipa import ClientMeta

# from python_freeipa import ClientMeta

import config
import globals
import urllib3

urllib3.disable_warnings()

# Setup logger
logger = logging.getLogger(__name__)


def save_json(file: str, data: dict):
    """
    Saves data to a JSON file, overwriting existing content.
    """
    try:
        with open(file, "w") as f:
            json.dump(data, f)
        logger.info(f"Successfully saved JSON to {file}")
    except Exception as e:
        logger.error(f"Failed to save JSON to {file}", exc_info=e)


def load_json(jsonfilename: str):
    """
    Loads data from a JSON file.
    """
    try:
        with open(jsonfilename, "r") as file:
            logger.info(f"Successfully loaded JSON from {jsonfilename}")
            return json.load(file)
    except Exception as e:
        logger.error(f"Failed to load JSON from {jsonfilename}", exc_info=e)


def ssh_gatekeeper(timestamp: str) -> str:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logger.info(f"Attempting SSH connection to {globals.config.gatekeeper.ip}")
        client.connect(
            globals.config.gatekeeper.ip,
            username=globals.config.gatekeeper.username,
            password=globals.config.gatekeeper.password,
        )

        command = globals.config.gatekeeper.command + f" --day {timestamp}"
        logger.info(f"Executing command on {globals.config.gatekeeper.ip}: {command}")
        stdin, stdout, stderr = client.exec_command(command)

        output = stdout.read().decode("utf-8")
        error = stderr.read().decode("utf-8")

        if output:
            logger.info(f"Command output: \n{output}")
            return f"```\n{output}\n```"
        if error:
            logger.error(f"Command error: \n{error}")
            return "Error: " + error
        return f"No data for day: {timestamp}"
    except Exception as e:
        logger.error("SSH connection or command execution failed", exc_info=e)
        return "Connection or execution failed."
    finally:
        client.close()

def ssh_print_server(timestamp: str, all: bool) -> bool:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logger.info(f"Attempting SSH connection to {globals.config.print_server.ip}")
        client.connect(
            globals.config.print_server.ip,
            username=globals.config.print_server.username,
            password=globals.config.print_server.password,
        )
        if all:
            command = globals.config.print_server.command + f" --day {timestamp}"  + f" --all"
        else:
            command = globals.config.print_server.command + f" --day {timestamp}"
        logger.info(f"Executing command on {globals.config.print_server.ip}: {command}")
        stdin, stdout, stderr = client.exec_command(command)

        output = stdout.read().decode("utf-8")
        error = stderr.read().decode("utf-8")

        if output:
            logger.info(f"Command output: \n{output}")
            return f"```\n{output}\n```"
        if error:
            logger.error(f"Command error: \n{error}")
            return "Error: " + error
        return f"No data for day: {timestamp}"
    except Exception as e:
        logger.error("SSH connection or command execution failed", exc_info=e)
        return "Connection or execution failed."
    finally:
        client.close()

async def ssh_vicuna(user: Member, prompt: str, channel: GuildChannel, reply_message: Message):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logger.info(f"Attempting SSH connection to {globals.config.vicuna.ip}")
        client.connect(
            globals.config.vicuna.ip,
            username=globals.config.vicuna.username,
            password=globals.config.vicuna.password,
        )
        command = globals.config.vicuna.command + f" --user {user.name} --prompt \"{prompt}\" --channel {channel.id}"
        logger.info(f"Executing command on {globals.config.vicuna.ip}: {command}")
        stdin, stdout, stderr = client.exec_command(command, timeout=300)
        output = stdout.read().decode("utf-8")
        error = stderr.read().decode("utf-8")
        if error:
            logger.error(f"Command error: \n{error}")
            await reply_message.edit("Error: " + error)
            return
        if output:
            output = output.replace("\\\\n", '\n').replace("\\n", '\n')
            logger.info(f"Command output: \n{output}")
            await reply_message.edit(output)
            logger.info(f"Responded to prompt")
            return
        await reply_message.edit("No data")
        logger.info(f"Failed with no data")
        return
    except Exception as e:
        logger.error("SSH connection or command execution failed", exc_info=e)
        await reply_message.edit("Connection or execution failed.")
        return
    finally:
        client.close()

async def get_response(client: Client, subject: Member, timeout=86400):
    def has_responded(message):
        # logger.info(f"Recieved dm: {message.author.id}, {subject.id}  {type(message.channel)}")
        return message.author.id == subject.id and isinstance(message.channel, nextcord.channel.DMChannel)

    try:
        reply = await client.wait_for("message", timeout=timeout, check=has_responded)
        logger.info(f"{subject.name} responded with {reply.content.strip()}")
        return reply.content.strip()
    except asyncio.TimeoutError:
        logger.warning(f"{subject.name} timed out")
        return None
    
async def timeout(subject: Member, dm_channel: DMChannel, output_channel: GuildChannel):
    await dm_channel.send('Conversation has timed out.  If you are still interested in becoming a CIF lab member, contact a CIF Tech Director')
    await output_channel.send(f'DM to {subject.name} timed out')
    logger.warning(f'DM to {subject.name} timed out')

async def prompt_first_name(client: Client, subject: Member, dm_channel: DMChannel) -> str:
    await dm_channel.send(f'What is your first name?')
    return await get_response(client, subject)

async def prompt_last_name(client: Client, subject: Member, dm_channel: DMChannel):
    await dm_channel.send(f'What is your last name?')
    return await get_response(client, subject)

async def prompt_netid(client: Client, subject: Member, dm_channel: DMChannel):
    await dm_channel.send(f'What is your NetID?')
    return await get_response(client, subject)

async def prompt_id(client: Client, subject: Member, dm_channel: DMChannel):
    await dm_channel.send(f'What is your student ID number?')
    id = await get_response(client, subject)
    if id is None:
        return None
    while not id.isdigit() or len(id) != 8:
        await dm_channel.send(f'\"{id}\" is not a valid student id number.  Try again')
        id = await get_response(client, subject)
        if id is None:
            return None
    return id

async def prompt_lcc(client: Client, subject: Member, dm_channel: DMChannel):
    await dm_channel.send(f'What is your LCC number?  It can be found above your picture on your student ID')
    id = await get_response(client, subject)
    if id is None:
        return None
    while not id.isdigit() or len(id) != 2:
        await dm_channel.send(f'\"{id}\" is not a valid LCC number.  Try again')
        id = await get_response(client, subject)
        if id is None:
            return None
    return id

async def prompt_class_year(client: Client, subject: Member, dm_channel: DMChannel):
    await dm_channel.send(f'What year do you graduate?')
    class_year = await get_response(client, subject)
    if class_year is None:
        return None
    while not class_year.isdigit() or len(class_year) != 4:
        await dm_channel.send(f'\"{class_year}\" is not a valid graduation year.  Try again')
        class_year = await get_response(client, subject)
        if class_year is None:
            return None
    return class_year

async def create_account(subject: Member, dm_channel: DMChannel, output_channel: GuildChannel, first_name: str, last_name: str, netid: str, id: str, lcc: str, class_year: str, member=False) -> int:
    try:
        citadel_client = ClientMeta(globals.config.citadel.ip, verify_ssl=globals.config.citadel.verify_ssl)
        citadel_client.login(globals.config.citadel.username, globals.config.citadel.password)
        logger.info(f'DM with {subject.name} successfully connected to citadel')
    except Exception as e:
        await dm_channel.send("Unable able to connect to Citadel.  Contact a tech director for support")
        await output_channel.send(f"DM with {subject.name} unable to connect to citadel")
        logger.warning(f"DM with {subject.name} unable to connect to citadel.  Error: {e}")
        return 2
    existing_users = citadel_client.user_find(o_employeenumber=id)['result']
    if len(existing_users) > 0:
        citadel_client.logout()
        await dm_channel.send(f"An account with the student id {id} already exists.  If you believe this to be in error, contact a tech director.  Otherwise, reconfirm your information")
        logger.warning(f"An account with the student id {id} already exists")
        return 1
    try:
        full_name = first_name + " " + last_name
        citadel_client.user_add(a_uid=netid, o_givenname=first_name, o_sn=last_name, o_cn = full_name, o_displayname=subject.name, o_employeenumber=id, o_employeetype=lcc, o_userpassword='cif314!', o_userclass=class_year)
        logger.info(f"Created lab account for {subject.name}")
        if member:
            citadel_client.group_add_member(a_cn="cif_full_members", o_user=netid)
        success_message = f'Your CIF Computer Lab Account has been created, and you now have swipe access to the lab!\n\nYour username is: {netid}\nYour temporary password is: cif314!\n\nPlease go to this website: https://citadel.cif.rochester.edu/\nLog in with your information, and set a new password.\n\nYour login is used for accessing CIF servers, logging in to lab computers, and printing from the print server.\nTo learn more about accessing CIF servers, see https://github.com/CIF-Rochester/wiki/wiki/Cage'
        await dm_channel.send(success_message)
        await output_channel.send(f'Lab account successfully created for {subject.name}')
        logger.info(f'{subject.name} completed the lab access process')
        return 0
    except Exception as e:
        await dm_channel.send(f"Unable to create lab account")
        return 2
    finally:
        citadel_client.logout()


async def dm_subject(client: Client, dm_channel: DMChannel, subject: nextcord.Member, output_channel: GuildChannel, member: bool = False):
    if member:
        opening_message = f'Dear {subject.name},\n As a CIF member, you are entitled to a CIF lab membership.  If you believe you have received this in error, please contact a CIF Tech Director and ignore this message.  Otherwise, even if you have no interest in the lab, please answer a few questions as this data helps CIF automate a number of different processes.  All responses should contain the relevant information, nothing more, and be made within 24 hours.'
    else:
        opening_message = f'Dear {subject.name},\n You have demonstrated an interest in becoming a CIF lab member.  If you believe you have received this in error, please contact a CIF Tech Director and ignore this message.  Otherwise, please answer a few questions.  All responses should contain the relevant information, nothing more, and be made within 24 hours.'
    await dm_channel.send(opening_message)
    first_name = await prompt_first_name(client, subject, dm_channel)
    if first_name is None:
        await timeout(subject, dm_channel, output_channel)
        return
    last_name = await prompt_last_name(client, subject, dm_channel)
    if last_name is None:
        await timeout(subject, dm_channel, output_channel)
        return
    netid = await prompt_netid(client, subject, dm_channel)
    if netid is None:
        await timeout(subject, dm_channel, output_channel)
        return
    id = await prompt_id(client, subject, dm_channel)
    if id is None:
        await timeout(subject, dm_channel, output_channel)
        return
    lcc = await prompt_lcc(client, subject, dm_channel)
    if lcc is None:
        await timeout(subject, dm_channel, output_channel)
        return
    class_year = await prompt_class_year(client, subject, dm_channel)
    if class_year is None:
        await timeout(subject, dm_channel, output_channel)
        return
    account_creation_code = 1
    while account_creation_code == 1:
        correct = False
        while not correct:
            await dm_channel.send(f'Thank you.  Please verify the following information:\n\nfirst_name: {first_name}\nlast_name: {last_name}\nnetid: {netid}\nid: {id}\nlcc: {lcc}\nclass_year: {class_year}\n\nIf all information is correct, reply \"yes\".  Otherwise specify the category you would like to change.')
            response = await get_response(client, subject)
            if response is None:
                await timeout(subject, dm_channel, output_channel)
                return
            elif response == 'yes':
                correct = True
            elif response == 'first_name':
                first_name = await prompt_first_name(client, subject, dm_channel)
                if first_name is None:
                    await timeout(subject, dm_channel, output_channel)
                    return
            elif response == 'last_name':
                last_name = await prompt_last_name(client, subject, dm_channel)
                if last_name is None:
                    await timeout(subject, dm_channel, output_channel)
                    return
            elif response == 'netid':
                netid = await prompt_netid(client, subject, dm_channel)
                if netid is None:
                    await timeout(subject, dm_channel, output_channel)
                    return
            elif response == 'id':
                id = await prompt_id(client, subject, dm_channel)
                if id is None:
                    await timeout(subject, dm_channel, output_channel)
                    return
            elif response == 'lcc':
                lcc = await prompt_lcc(client, subject, dm_channel)
                if lcc is None:
                    await timeout(subject, dm_channel, output_channel)
                    return
            elif response == 'class_year':
                class_year = await prompt_class_year(client, subject, dm_channel)
                if class_year is None:
                    await timeout(subject, dm_channel, output_channel)
                    return
        account_creation_code = await create_account(subject, dm_channel, output_channel, first_name, last_name, netid, id, lcc, class_year, member=member)
    if account_creation_code == 0:
        lab_member_role = nextcord.utils.get(output_channel.guild.roles, name="Lab Members")
        await subject.add_roles(lab_member_role)

def get_all_accounts(citadel_client: ClientMeta):
    try:
        logger.info(f'Successfully connected to citadel')
        return citadel_client.user_find(o_sizelimit=0)['result']
    except Exception as e:
        return None

def has_graduated(user, current_date: date):
    if 'userclass' in user:
        delta = current_date - date(int(user['userclass'][0]), 6, 1)
        return delta.total_seconds() >= 0
    return False

async def set_primary_role(subject: Member, role: Role, friend_role: Role, member_role: Role, alumni_role: Role):
    updated_discord = False
    subject_roles = subject.roles
    if not nextcord.utils.get(subject_roles, name=role.name):
        await subject.add_roles(role)
        logger.info(f"Gave {role.name} role to {subject.name}")
        updated_discord = True
    if not role.name == "Friends" and nextcord.utils.get(subject_roles, name="Friends"):
        await subject.remove_roles(friend_role)
        logger.info(f"Removed Friends role from {subject.name}")
        updated_discord = True
    if not role.name == "Members" and nextcord.utils.get(subject_roles, name="Members"):
        await subject.remove_roles(member_role)
        logger.info(f"Removed Members role from {subject.name}")
        updated_discord = True
    if not role.name == "Alumni" and nextcord.utils.get(subject_roles, name="Alumni"):
        await subject.remove_roles(alumni_role)
        logger.info(f"Removed Alumni role from {subject.name}")
        updated_discord = True
    return updated_discord

async def update_members(guild: Guild, current_date: date) -> str:
    try :
        citadel_client = ClientMeta(globals.config.citadel.ip, verify_ssl=globals.config.citadel.verify_ssl)
        citadel_client.login(globals.config.citadel.username, globals.config.citadel.password)
    except Exception as e:
        return "Unable to connect to citadel"
    users = get_all_accounts(citadel_client)
    output = ""
    counter = 0
    friend_role = nextcord.utils.get(guild.roles, name="Friends")
    lab_member_role = nextcord.utils.get(guild.roles, name="Lab Members")
    member_role = nextcord.utils.get(guild.roles, name="Members")
    alumni_role = nextcord.utils.get(guild.roles, name="Alumni")
    for user in users:
        try:
            updated_citadel = False
            subject = guild.get_member_named(user['displayname'][0])
            uid = user['uid'][0]
            graduated = has_graduated(user, current_date)
            locked = user['nsaccountlock']
            groups = user['memberof_group']
            if graduated:
                if not locked:
                    citadel_client.user_disable(uid)
                    updated_citadel = True
                if "cif_full_members" in groups:
                    citadel_client.group_remove_member(a_cn="cif_full_members", o_user=uid)
                    updated_citadel = True
                if "users" in groups:
                    citadel_client.group_remove_member(a_cn="users", o_user=uid)
                    updated_citadel = True
                if not "cif_alumni" in groups:
                    citadel_client.group_add_member(a_cn="cif_alumni", o_user=uid)
                    updated_citadel = True
            if updated_citadel:
                logger.info(f"Updated user {uid} in citadel")
            updated_discord = False
            if subject and not locked:
                subject_roles = subject.roles
                for group in groups:
                    if group == 'cif_full_members':
                        if graduated:
                            updated_discord = updated_discord or await set_primary_role(subject, alumni_role, friend_role, member_role, alumni_role)
                        else:
                            updated_discord = updated_discord or await set_primary_role(subject, member_role, friend_role, member_role, alumni_role)
                    if group == 'users':
                        if graduated and nextcord.utils.get(subject.roles, name="Lab Members"):
                            await subject.remove_roles(lab_member_role)
                            updated_discord = True
                        elif not graduated and not nextcord.utils.get(subject_roles, name="Lab Members"):
                            await subject.add_roles(lab_member_role)
                            updated_discord = True
                if updated_discord:
                    logger.info(f"Updated discord account {subject.name} associated with {uid}")
            if updated_citadel:
                output += f"Updated user {uid} in citadel"
            if updated_citadel and updated_discord:
                output += ", "
            if updated_discord:
                output += f"Updated user {subject.name} in discord"
            if updated_discord or updated_citadel:
                output += "\n"
        except Exception as e:
            output += f"Failed to update {user['cn'][0]}  Error: {e}\n"
            logger.warning(f"Failed to update {user['cn'][0]}  Error: {e}")
            return f"Error: {e}  {str(user)}"
    if not output:
        output = "No users updated"
    citadel_client.logout()
    return output

async def remove_member(subject: Member, guild: Guild):
    member_role = nextcord.utils.get(subject.roles, name="Members")
    if member_role:
        await subject.remove_roles(member_role)
        logger.info(f"Removed Members role from {subject.name}")
    friend_role = nextcord.utils.get(guild.roles, name="Friends")
    if not nextcord.utils.get(subject.roles, name="Friends"):
        await subject.add_roles(friend_role)
        logger.info(f"Gave Friends role to {subject.name}")
    try :
        citadel_client = ClientMeta(globals.config.citadel.ip, verify_ssl=globals.config.citadel.verify_ssl)
        citadel_client.login(globals.config.citadel.username, globals.config.citadel.password)
    except Exception as e:
        return "Unable to connect to citadel"
    user = citadel_client.user_find(o_displayname=subject.name)['result']
    if len(user) > 0:
        citadel_client.group_remove_member(a_cn="cif_full_members", o_user=user[0]['uid'][0])
    citadel_client.logout()
    return f"Successfully removed {subject.name} from member list"
