import argparse
import smtplib
import socket
import time
from datetime import datetime, timedelta

__help__ = "Module to check smtp"
__requirements__ = "cryptography"


def add_common_args(parser):
    parser.add_argument(
        "--hostname", "-H",
        action="store",
        dest="hostname",
        required=True,
        help="Hostname, IP or domain of the target"
    )
    parser.add_argument(
        "--port", "-p",
        action="store",
        dest="port",
        type=int,
        default=25,
        help="Port of SMTP server. (default: %(default)s)"
    )
    parser.add_argument(
        "--timeout",
        action="store",
        dest="timeout",
        type=int,
        default=10,
        help="Default timeout for connection attempt. (default: %(default)s)"
    )


def mode_connect(utils, debug):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--start-tls",
        action="store_true",
        dest="start_tls",
        help="Specify if STARTTLS should be used"
    )
    parser.add_argument(
        "--ssl",
        action="store_true",
        dest="ssl",
        help="Specify if SMTPS should be used"
    )
    config = parser.parse_known_args()[0]
    start = time.time()
    try:
        if config.ssl:
            with smtplib.SMTP_SSL(host=config.hostname, port=config.port, timeout=config.timeout) as client:
                res = client.noop()
        else:
            with smtplib.SMTP(host=config.hostname, port=config.port, timeout=config.timeout) as client:
                if config.start_tls:
                    client.starttls()
                res = client.noop()
        connection_time = time.time() - start
        if res == (250, b'2.0.0 Ok'):
            utils.build_output(
                state=utils.OutputState.OK, output=f"Connection to {config.hostname} established.",
                datasets=[
                    utils.build_dataset(name="Connection time", value=connection_time)
                ]
            )
        else:
            utils.build_output(
                state=utils.OutputState.CRITICAL,
                output=f"Connection to {config.hostname} established, but response was {str(res)}",
                datasets=[
                    utils.build_dataset(name="Connection time", value=connection_time)
                ]
            )
    except smtplib.SMTPServerDisconnected:
        utils.build_output(state=utils.OutputState.UNKNOWN, output=f"Connection to {config.hostname} timed out")


def mode_login(utils, debug):
    parser = argparse.ArgumentParser()
    add_common_args(parser)
    parser.add_argument(
        "--smtp-user",
        action="store",
        required=True,
        dest="smtp_user",
        help="Username to authenticate with"
    )
    parser.add_argument(
        "--smtp-password",
        action="store",
        required=True,
        dest="smtp_password",
        help="Password to authenticate with"
    )
    parser.add_argument(
        "--start-tls",
        action="store_true",
        dest="start_tls",
        help="Specify if STARTTLS should be used"
    )
    parser.add_argument(
        "--ssl",
        action="store_true",
        dest="ssl",
        help="Specify if SMTPS should be used"
    )
    config = parser.parse_known_args()[0]
    start = time.time()
    try:
        try:
            if config.ssl:
                with smtplib.SMTP_SSL(host=config.hostname, port=config.port, timeout=config.timeout) as client:
                    res = client.login(config.smtp_user, config.smtp_password)
            else:
                with smtplib.SMTP(host=config.hostname, port=config.port, timeout=config.timeout) as client:
                    res = client.login(config.smtp_user, config.smtp_password)
        except smtplib.SMTPServerDisconnected:
            utils.build_output(
                state=utils.OutputState.UNKNOWN,
                output=f"Connection to {config.hostname} timed out."
            )
    except smtplib.SMTPAuthenticationError:
        # Set res to 535 as that's the code for Authentication failed in SMTP
        res = (535,)
    connection_time = time.time() - start
    if res == (235, b'2.7.0 Authentication successful'):
        utils.build_output(
            state=utils.OutputState.OK, output=f"Authentication successful",
            datasets=[utils.build_dataset(name="Connection time", value=connection_time)]
        )
    elif res[0] == 535:
        utils.build_output(
            state=utils.OutputState.CRITICAL, output="Authentication failed",
            datasets=[utils.build_dataset(name="Connection time", value=connection_time)]
        )


def mode_sendmail(utils, debug):
    parser = argparse.ArgumentParser()
    add_common_args(parser)
    parser.add_argument(
        "--start-tls",
        action="store_true",
        dest="start_tls",
        help="Specify if STARTTLS should be used"
    )
    parser.add_argument(
        "--ssl",
        action="store_true",
        dest="ssl",
        help="Specify if SMTPS should be used"
    )
    parser.add_argument(
        "--smtp-user",
        action="store",
        required=True,
        dest="smtp_user",
        help="Username to authenticate with"
    )
    parser.add_argument(
        "--smtp-password",
        action="store",
        required=True,
        dest="smtp_password",
        help="Password to authenticate with"
    )
    parser.add_argument(
        "--from",
        action="store",
        required=True,
        dest="smtp_from",
        help="From address for mail"
    )
    parser.add_argument(
        "--to",
        action="store",
        required=True,
        dest="smtp_to",
        help="To address for mail"
    )
    parser.add_argument(
        "--msg",
        action="store",
        required=True,
        dest="smtp_msg",
        help="Message to send in mail"
    )
    config = parser.parse_known_args()[0]
    try:
        try:
            if config.ssl:
                with smtplib.SMTP_SSL(host=config.hostname, port=config.port, timeout=config.timeout) as client:
                    res = client.login(config.smtp_user, config.smtp_password)
                    if res[0] == 235:
                        res = client.sendmail(config.smtp_from, config.smtp_to, config.smtp_msg.replace("\\n", "\n"))
                        if res == {}:
                            utils.build_output(
                                state=utils.OutputState.OK,
                                output="Message was sent"
                            )
                        else:
                            utils.build_output(
                                state=utils.OutputState.UNKNOWN,
                                output=f"Message could not be sent: {res}"
                            )
            else:
                with smtplib.SMTP(host=config.hostname, port=config.port, timeout=config.timeout) as client:
                    if config.start_tls:
                        client.starttls()
                    res = client.login(config.smtp_user, config.smtp_password)
                    if res[0] == 235:
                        res = client.sendmail(config.smtp_from, config.smtp_to, config.smtp_msg.replace("\\n", "\n"))
                        if res == {}:
                            utils.build_output(
                                state=utils.OutputState.OK,
                                output="Message was sent"
                            )
                        else:
                            utils.build_output(
                                state=utils.OutputState.UNKNOWN,
                                output=f"Message could not be sent: {res}"
                            )
        except smtplib.SMTPAuthenticationError:
            utils.build_output(
                state=utils.OutputState.UNKNOWN,
                output="Authentication failed"
            )
    except smtplib.SMTPServerDisconnected:
        utils.build_output(
            state=utils.OutputState.UNKNOWN,
            output=f"Connection to {config.hostname} timed out."
        )


def mode_certificate(utils, debug):
    from cryptography import x509
    parser = argparse.ArgumentParser()
    add_common_args(parser)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--start-tls",
        action="store_true",
        dest="start_tls",
        help="Specify if STARTTLS should be used"
    )
    group.add_argument(
        "--ssl",
        action="store_true",
        dest="ssl",
        help="Specify if SMTPS should be used"
    )
    parser.add_argument(
        "--warning-expiry",
        action="store",
        dest="warning_expiry",
        default=20,
        type=int,
        help="Warning threshold (default: %(default)s)"
    )
    parser.add_argument(
        "--critical-expiry",
        action="store",
        dest="critical_expiry",
        default=10,
        type=int,
        help="Critical threshold (default: %(default)s)"
    )
    config = parser.parse_known_args()[0]
    try:
        if config.ssl:
            with smtplib.SMTP_SSL(host=config.hostname, port=config.port, timeout=config.timeout) as client:
                cert_decoded = x509.load_der_x509_certificate(client.sock.getpeercert(binary_form=True))
        else:
            with smtplib.SMTP(host=config.hostname, port=config.port, timeout=config.timeout) as client:
                # starttls can be called, because mode certificate use either --ssl or --start-tls as options
                client.starttls()
                cert_decoded = x509.load_der_x509_certificate(client.sock.getpeercert(binary_form=True))
    except socket.timeout:
        utils.build_output(state=utils.OutputState.UNKNOWN, output=f"Connection to {config.hostname} timed out")
    now = datetime.utcnow()
    critical = now + timedelta(days=config.critical_expiry)
    critical_due = cert_decoded.not_valid_after - critical
    if critical_due.total_seconds() <= 0:
        utils.build_output(
            state=utils.OutputState.CRITICAL,
            output=f"Certificate is valid {(cert_decoded.not_valid_after - now).days} days"
        )
    warning = now + timedelta(days=config.warning_expiry)
    warning_due = cert_decoded.not_valid_after - warning
    if warning_due.total_seconds() <= 0:
        utils.build_output(
            state=utils.OutputState.WARN,
            output=f"Certificate is valid {(cert_decoded.not_valid_after - now).days} days"
        )
    utils.build_output(
        state=utils.OutputState.OK,
        output=f"Certificate is valid {(cert_decoded.not_valid_after - now).days} days"
    )


def execute(utils, debug=False):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--mode",
        choices=["connect", "login", "sendmail", "certificate"],
        action="store",
        dest="mode",
        required=True,
        help="Set mode the plugin should execute"
    )
    config = parser.parse_known_args()[0]
    if config.mode == "connect":
        mode_connect(utils, debug)
    elif config.mode == "login":
        mode_connect(utils, debug)
    elif config.mode == "sendmail":
        mode_sendmail(utils, debug)
    elif config.mode == "certificate":
        mode_certificate(utils, debug)
