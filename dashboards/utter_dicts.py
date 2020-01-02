# import string
# import re
# import pandas as pd
# import numpy as np
# from collections import defaultdict

# import spacy
# from spacy import displacy
# from spacy.matcher import Matcher
# from spacy.lemmatizer import Lemmatizer
# from spacy.lookups import Lookups


text_to_list = lambda t: t.replace(' ', '').replace('\n', '').split(',')


FAMILY = {
    'accounts': text_to_list("""
                bonus interest account,
                business account,
                business savings account,
                child account,
                child savings account,
                current account,
                g account,
                grow bigger account,
                life-course account,
                loan joint account,
                orange savings account,
                pension savings account,
                profit savings account,
                salary savings account,
                savings account,
                savings account (joint),
                student account,
                top account,
                youth account,
                youth savings account,
                orange package,
                royal package,
                special offer,
                account
                """),
    'cards': text_to_list("""
                credit card,
                credit card (student),
                debit card,
                debit card - joint account,
                debit card - world,
                debit card business,
                ing credit card business,
                mastercard,
                prepaid credit card,
                visa,
                card
                """),
    'ing_store': text_to_list("""
                coins,
                gift card,
                voucher,
                points,
                ing store
                """),
    'insurances': text_to_list("""
                accident insurance,
                annuity insurance,
                bicycle insurance,
                business insurance,
                cancellation insurance,
                capital insurance,
                car insurance,
                custom insurance,
                funeral insurance,
                house-contents insurance,
                housing insurance,
                legal insurance,
                liability insurance,
                life insurance,
                travel insurance,
                student insurance,
                term life insurance,
                pension,
                insurance
                """),
    'investments': text_to_list("""
                asset management,
                investement property,
                investment account,
                investment fund,
                investment mortgage,
                investment portfolio,
                securities,
                shares,
                ing triodos greenfund,
                investment
                """),
    'loans': text_to_list("""
                business loan,
                car loan,
                mortgage bridge loan,
                personal loan,
                student loan,
                loan
                """),
    'mortgages': text_to_list("""
                added value mortgage,
                annuity mortgage,
                bank savings mortgage,
                bullet mortgage,
                interest only mortgage,
                mortgage
                """),
    'payments': text_to_list("""
                cash,
                deposito,
                direct debit,
                foreign money,
                income supplement depot,
                interim credit,
                revolving credit,
                payment
                """),
    'undefined': text_to_list("""
                life testament,
                vault,
                undefined
                """),
}


#
PRODUCT_ATTR = {
    'apply': text_to_list("""
                australian dollars,
                cancellation,
                change,
                changes,
                credit,
                deferral,
                expansion,
                extra,
                extra card,
                extra deposit,
                extra mortage,
                foreign money,
                increase,
                interim credit,
                new card,
                order,
                prolongation,
                promotion,
                refund,
                rejection,
                release,
                repairment,
                retrieval,
                return,
                settlement,
                supplement,
                surplus value,
                update,
                update form,
                withdrawal,
                withdrawal (abroad - costs),
                withdrawal (abroad),
                withdrawal (large amount),
                withdrawal (without card),
                withhold,
                withhold (abroad),
                apply
                """),
    'location': text_to_list("""
                location, settings,
                abroad,
                abroad (out EU),
                destination,
                language settings,
                opening hours,
                origin,
                translation,
                location
                """),
    'transaction': text_to_list("""
                additional repayment,
                additional repayment (this year),
                automatic saving,
                contactless payments (NFC),
                deposit,
                deposit (costs),
                deposit (large amount),
                direct debit,
                double payment,
                extra repayment,
                from_cc,
                installment payment,
                instant payments,
                payment,
                payment (abroad),
                payment arrears,
                payment duration,
                payment info,
                payment plan,
                payment reminder,
                payment request,
                priority transfer,
                repayment,
                repayment confirmation,
                repayment note,
                repayment partial,
                repayment table,
                to_cc,
                to_coins,
                to_currentacc,
                to_investacc,
                to_savingsacc,
                transfer,
                transfer booklet,
                transaction
                """),
    'contract': text_to_list("""
                agreement,
                duration,
                end of term,
                enddate,
                execution date,
                expiration,
                liability,
                period,
                pledge,
                policy,
                possible fraud,
                seizure,
                waranty,
                contract
                """),
    'verification': text_to_list("""
                access,
                access code,
                activation code,
                authorization,
                bank guarantee,
                certificate,
                code,
                confirmation,
                confirmation code,
                login code,
                pincode,
                privacy,
                secure code,
                security,
                security camera footage,
                signature,
                swift code,
                tan codes,
                user name password,
                verification code,
                without_authorization
                """),
    'communication': text_to_list("""
                collection message,
                correspondence,
                mail (for other person),
                mail (not delivered),
                communication
                """),
    'statement': text_to_list("""
                statement,
                statement (cancellation),
                statement (current balance),
                statement (financing),
                statement (fiscally),
                statement (purchase),
                statement (quarterly),
                statement (solvency),
                statement (yearly),
                statement folder,
                status,
                buy off statement,
                salary information,
                saving goal,
                scheduled tasks,
                specific transaction reporting,
                statement
                """),
    'state': text_to_list("""
                application state,
                state_blocked,
                state_closed,
                state_refused,
                state
                """),
    'profile': text_to_list("""
                account,
                account holder,
                account name,
                account number,
                account type,
                address,
                begunstigde,
                bic,
                bkr registration,
                contact details,
                delivery address,
                email address,
                extra account,
                iban,
                identity information,
                inbox,
                legal representative,
                linked account,
                linked_account,
                name,
                new phone,
                note,
                personal details,
                phone number,
                profile
                """),
    'limit': text_to_list("""
                limit (abroad - withdraw),
                limit (abroad),
                limit (daily - temporary),
                limit (daily - withdraw),
                limit (daily),
                limit (temporary),
                limit (withdraw),
                limit
                """),
    'investment': text_to_list("""
                building depot,
                buy,
                buy off,
                capital accumulation,
                debt/market value,
                ground lease,
                market value,
                market value change,
                market/value ratio,
                pay off,
                pay out,
                payout,
                purchase,
                refinance,
                refinance fine,
                risk class,
                sale,
                second building,
                investment
                """),
    'interest': text_to_list("""
                interest (change),
                interest (fixed rate period),
                interest (middle out),
                interest change,
                interest prolongation,
                risk premium interest,
                interest
                """),
    'insurance': text_to_list("""
                coverage,
                coverage (abroad),
                coverage (worldwide),
                damaged,
                found card,
                lost,
                lost and found,
                insurance
                """),
    'undefined': text_to_list("""
                advise,
                calculation,
                delivery,
                description,
                envelopes,
                form,
                info,
                installment note,
                large denominations,
                lender,
                management,
                points,
                premium,
                reservation,
                specific item,
                type,
                voucher,
                undefined
                """),
    'value': text_to_list("""
                amount,
                balance,
                claim,
                cost,
                costs,
                costs (abroad),
                debt,
                discount,
                dividend,
                exchange,
                fine,
                large amount,
                number,
                price,
                quotation,
                residual debt,
                tax,
                value
                """),
}

# CRUD like
ACTION = {
    'create': text_to_list("""
                open,
                activate,
                apply, apply channel,
                block,
                complain,
                sign,
                create
                """),
    'read': text_to_list("""
                inform, inform channel, inform new,
                check, check channel, verify,
                supply,
                receive,
                read
                """),
    'update': text_to_list("""
                change,
                reduce,
                increase,
                replace,
                merge,
                update
                """),
    'delete': text_to_list("""
                end,
                delete
                """),
    'undefined': text_to_list("""
                don't know,
                undefined
                """),
}


# State like
ACTION_ATTR = {
    'failed': text_to_list("""
                outage,
                install,
                not succeed,
                log in,
                failure,
                failed
                """),
    'rejected': text_to_list("""
                not approved,
                not confirmed, unconfirmed,
                not debited,
                not retrieved,
                state_blocked,
                state_closed,
                insufficient funds,
                rejected
                """),
    'missing': text_to_list("""
                update,
                without card,
                fingerprint,
                forgotten, forgot,
                signiture & stamp,
                id means,
                driving license,
                client abroad,
                missing
                """),
    'unclear': text_to_list("""
                opening hours,
                vacancies,
                unclear
                """),
    'undo': text_to_list("""
                unblock,
                cancel,
                stop,
                undo
                """),
    'undefined': text_to_list("""
                don't understand,
                undefined
                """),
}

CHANNEL = {
    'atm': text_to_list("""
                atm deposit,
                atm non-ING,
                atm
                """),
    'branch': text_to_list("""
                servicepoint,
                headquarters,
                department,
                appointment,
                branch
                """),
    'web': text_to_list("""
                online,
                online banking,
                shop, webshop,
                web
                """),
    'app': text_to_list("""
                online banking mobile app,
                online banking mobile app Android,
                online banking mobile app iOS,
                app
                """),
    'other_digital': text_to_list("""
                email,
                sms,
                tikkie,
                ideal,
                apple pay,
                paypal,
                scanner,
                digital
                """),
    'other_non_digital': text_to_list("""
                advise,
                mail, letter,
                phone,
                balance line,
                zoomit,
                western union,
                post office,
                other
                """),
    'undefined': text_to_list("""
                don't know,
                undefined
                """),
}


# Tag colours
COLORS = ["#67E568", "#257F27", "#08420D", "#FFF000", "#FFB62B",
          "#E56124", "#E53E30", "#7F2353", "#F911FF", "#9F8CA6"]


FAMILY_COLORS = {k.upper(): COLORS[0] for k in FAMILY.keys()}
PRODUCT_ATTR_COLORS = {k.upper(): COLORS[1] for k in PRODUCT_ATTR.keys()}
CHANNEL_COLORS = {k.upper(): COLORS[5] for k in CHANNEL.keys()}
ACTION_COLORS = {k.upper(): COLORS[3] for k in ACTION.keys()}
ACTION_ATTR_COLORS = {k.upper(): COLORS[4] for k in ACTION_ATTR.keys()}
ENTITY_COLORS = {f'ENTITY': COLORS[6] for i in range(10)}
ROOT_COLORS = {'ROOT': COLORS[8]}

POS = {
       **FAMILY_COLORS,
       **PRODUCT_ATTR_COLORS,
       **CHANNEL_COLORS,
       **ACTION_COLORS,
       **ACTION_ATTR_COLORS,
       **ENTITY_COLORS,
       **ROOT_COLORS
       }