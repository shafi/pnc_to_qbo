import csv
import glob
import yaml


def debit(t):
    if t=='DEBIT':
        return -1.0
    else:
        return 1.0

def addTransaction(row,fitid):
    d = row[0].replace("/","")
    if d in fitid:
        fitid[d] = fitid[d]+1
    else:
         fitid[d] = 1
    if row[3]=="":
        memo=row[2]
    else:
        memo=row[3]
    t = ("<STMTTRN>\n" +
		"<TRNTYPE>{0}\n".format(row[5]) +
		"<DTPOSTED>{0}120000\n".format(d) +
		"<DTUSER>{0}120000\n".format(d) +
		"<TRNAMT>{0}\n".format(float(row[1])*debit(row[5])) +
		"<FITID>{0}{1}\n".format(conf['account'],d+str(fitid[d])) +
		"<NAME>{0}\n".format(row[2][:30]) +
		"<MEMO>{0}\n".format(memo) +
		"</STMTTRN>\n")
    return t

def process_stmt(f):
    qbo = """
OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET:1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE

<OFX>
<SIGNONMSGSRSV1>
<SONRS>
<STATUS>
<CODE>0
<SEVERITY>INFO
</STATUS>
<DTSERVER>20160211223445.051[-5:EST]
<LANGUAGE>ENG
<FI>
<ORG>PNC
<FID>7138
</FI>
<INTU.BID>7138
<INTU.USERID>123456789
</SONRS>
</SIGNONMSGSRSV1>
<BANKMSGSRSV1>
<STMTTRNRS>
<TRNUID>0
<STATUS>
<CODE>0
<SEVERITY>INFO
</STATUS>
<STMTRS>
<CURDEF>USD
<BANKACCTFROM>
<BANKID>{0}
<ACCTID>0000000000{1}
<ACCTTYPE>CHECKING
</BANKACCTFROM>
<BANKTRANLIST>
<DTSTART>19700101120000
<DTEND>20161230120000
""".format(conf['bankid'],conf['account'])
    i= 0
    fitid = {}
    with open(f, newline='') as csvfile:
        stmt = csv.reader(csvfile)
        first = next(stmt)
        for row in stmt:
            i=i+1
            qbo = qbo + ''.join(addTransaction(row,fitid))

    qbo_end = ("</BANKTRANLIST>\n" +
               "<LEDGERBAL>\n" +
               "<BALAMT>{0}\n".format(first[4]) +
               "<DTASOF>{0}120000\n".format(first[2].replace("/","")) +
               "</LEDGERBAL>\n" +
               "</STMTRS>\n" +
               "</STMTTRNRS>\n" +
               "</BANKMSGSRSV1>\n" +
               "</OFX>")

    qbo = qbo + ''.join(qbo_end)

    with open(conf['stmt_folder']+f.replace('csv','qbo'), "w") as text_file:
        print(qbo, file=text_file)


if if __name__ == "__main__":
    conf = yaml.load(open('pnc_to_qbo.yaml'))
    for f in glob.glob(conf['stmt_folder']+"*.csv"):
        print(f)
        process_stmt(f)