#GUItemplate.py
from tkinter import *
from tkinter import ttk
from tkinter.ttk import Notebook
###### Firebase Setting ##################
from firebase import firebase
from datetime import datetime
from tkinter import messagebox
from threading import Thread
import webbrowser

FONT = ('Angsana New',15)

firebase = firebase.FirebaseApplication('https://unclestore-180bd.firebaseio.com/')

urlfirebase = 'https://console.firebase.google.com/project/unclestore-180bd/database/unclestore-180bd/data/~2F'

###### Function Send to Firebase ##################
def SendtoFirebase(): # เพื่อส่งข้อมูลขึ้น Firebase Server บน Internet 
	global buffer_product
	table_sales.delete(*table_sales.get_children()) # ลบข้อมูลใน Table ออกให้หมด
	v_total.set('0.00')
	keyid = datetime.now().strftime('%Y%m%d_%H%M%S')
	send = firebase.put('/History',keyid,buffer_product)
	print('DATA TO FIREBASE',send)

	################ Update Data #################################
	RunUpdateProductTable() # เพื่อเช็คว่าสต็อคล่าสุด Update เป็นจำนวนเท่าไร 
	for bfk,bfv in buffer_product.items():
		try:
			new_quan = stockproduct[bfk]['pdquan'] - bfv[2]
			new_total = stockproduct[bfk]['total'] - bfv[-1]
			data_update = {'pdquan':new_quan,'total':new_total}
			update = firebase.patch('/Allproduct/'+ bfk,data_update)
		except:
			print('ERROR UPDATE: ',bfv)
	################################
	# RunUpdateProductTable()
	UpdateMbPointandCredit()
	v_status.set(f'Record: {keyid} - Done!') #messagebox.showinfo('Done','ส่งข้อมูลสำเร็จ')
	buffer_product = {}

###### Threading ##################
def RunSendtoFirebase():
	v_status.set('Uploading...')
	thread1 = Thread(target=SendtoFirebase) # ใช้ Thread ช่่วยในการทำงานคู่ขนานกัน
	thread1.start()

############# Set Up GUI ###########
GUI = Tk()
GUI.geometry('900x590+0+0')
GUI.title('My Program')
#GUI.state('zoomed')

######################### Full Screen ##################

fullscreen = False
GUI.attributes("-fullscreen", fullscreen)

def BacktoNormal(event=None):
	global fullscreen
	#global ทำให้สามารถกำหนดค่าใหม่ที่อยู่นอกฟังก์ชั่นได้
	fullscreen = not fullscreen
	GUI.attributes("-fullscreen",fullscreen)

GUI.bind('<F11>',BacktoNormal)

########### MAIN MENU ###################

menubar = Menu(GUI)
GUI.config(menu=menubar)

filemenu = Menu(menubar,tearoff=0) # FILE MENU
menubar.add_cascade(label='File',menu=filemenu)
#filemenu.add_command(label='Exit Program',command=GUI.quit) # GUI.quit เป็นคำสั่งที่จะปิดโปรแกรม
filemenu.add_command(label='Exit Program',command=lambda: GUI.withdraw()) # lambda คือการทำให้ฟังก์ชั่น สามารถรันในบรรทัดเดียว
filemenu.add_command(label='Open Firebase',command=lambda: webbrowser.open(urlfirebase))

helpmenu = Menu(menubar,tearoff=0) # HELP MENU
menubar.add_cascade(label='Help',menu=helpmenu)
helpmenu.add_command(label='Donate',
	command=lambda: messagebox.showinfo('Donate','บัญชี XXXXX \nจำนวนเงิน YYYYY บาท'))

################# TAB #############

Tab = Notebook(GUI)

F1 = Frame(Tab)
F2 = Frame(Tab)
F3 = Frame(Tab)
F4 = Frame(Tab)

img_sales = PhotoImage(file='tab-sales.png')
img_product = PhotoImage(file='tab-product.png')
img_history = PhotoImage(file='tab-history.png')
img_member = PhotoImage(file='tab-member.png')

Tab.add(F1,text='		Sales       ', image=img_sales, compound='top')
Tab.add(F2,text='		Product     ', image=img_product, compound='top')
Tab.add(F3,text='		History     ', image=img_history, compound='top')
Tab.add(F4,text='		Member     ', image=img_member, compound='top')

Tab.pack(fill=BOTH,expand=1) ## End Tab

##########Button Coffee ##############
F1LB1 = ttk.LabelFrame(F1,text='All Coffee')
F1LB1.place(x=20,y=15)

####### Button Function ##########

buffer_product = {}


########### Product Information ##################
productmenu = {'b1001':{'pid':'b1001','price':40,'name':'Espresso'},
			   'b1002':{'pid':'b1002','price':45,'name':'Americano'},
			   'b1003':{'pid':'b1003','price':50,'name':'Mocca'},
			   'b1004':{'pid':'b1004','price':60,'name':'Cappuccino'},
			   'b1005':{'pid':'b1005','price':40,'name':'Latte'},
			   'b1006':{'pid':'b1006','price':70,'name':'Chocolate'},
			   'b1007':{'pid':'b1007','price':80,'name':'Caramel Macciato'},
			   'b1008':{'pid':'b1008','price':90,'name':'White Chocolate'},
			   'b1009':{'pid':'b1009','price':50,'name':'Hot Tea'},
			   }

# productname = {}
# for k,v in productmenu.items():
#	productname[v['name']] = k

# print('PDNAME: ',productname)

############ Update Latest Data ################

def Update_table():
	### ลบข้อมูลเก่าใน Table ออก แล้วใส่ข้อมูลใหม่ที่พึ่ง Update เข้าไป ##########
	table_sales.delete(*table_sales.get_children()) # ลบข้อมูลใน Table ออกให้หมด
	for bp in buffer_product.values():
		# ดึงค่าล่าสุดจาก buffer_product เอามาเฉพาะ value เพื่อมาใส่เข้าไปใน Table
		table_sales.insert('','end',value=bp)

def InsertTable(product):
	global buffer_product # ทำให้สามารถแก้ไขตัวแปรภายนอกฟังก์ชั่นได้
	# product = 'espresso'
	if product not in buffer_product:
		# หากไม่มีสินค้าในรายการซื้อครั้งนี้ จะทำขั้นตอนนี้
		pid = productmenu[product]['pid']
		pdname = productmenu[product]['name']
		pdprice = productmenu[product]['price']
		quan = 1
		total = quan * pdprice
		rw = [pid,pdname,quan,pdprice,total]
		buffer_product[product] = rw # เก็บไว้ชั่วคราว
		try: 
			for bp in buffer_product.items():
				if bp[1][1] == 'Cash Discount':
					cdkey = bp[1][0]
					cdlist = bp[1]
			buffer_product.pop(cdkey)
			buffer_product[cdkey] = cdlist
		except:
			pass
	else:
		# หากสินค้ามีแล้ว เราจะทำการแก้ไขใหม่
		old = buffer_product[product] # เป็น List ['espresso',1,50,50]
		quan = old[2] + 1 # Index ที่ 0 คือ espresso Index ที่ 1 คือ จำนวน เท่ากับ 1 ดึงค่าเก่ามาบวกอีก 1
		newtotal = quan * old[3] # Index ที่ 2 คือ ราคา
		new = [old[0],old[1],quan,old[3],newtotal]
		buffer_product[product]= new

	### ลบข้อมูลเก่าใน Table ออก แล้วใส่ข้อมูลใหม่ที่พึ่ง Update เข้าไป ##########
	table_sales.delete(*table_sales.get_children()) # ลบข้อมูลใน Table ออกให้หมด
	for bp in buffer_product.values():
		# ดึงค่าล่าสุดจาก buffer_product เอามาเฉพาะ value เพื่อมาใส่เข้าไปใน Table
		table_sales.insert('','end',value=bp)

	SumTotal()
	total1 = []
	for k,v in buffer_product.items():
		total1.append(v[-1])
	total1 = sum(total1)
	discount = []
	for bp in buffer_product.items():
		if bp[1][1] == 'Cash Discount':
			discount.append(bp[1][-1])
	discount = -(sum(discount))
	total2 = total1 + discount
	netamount = total1
	creditpayment = int(v_creditpayment.get())
	cashpayment = netamount - creditpayment
	v_total2.set(total2)
	v_netamount.set(netamount)
	v_cashpayment.set(cashpayment)
	
	print('------------')
	print('Buffer Product : ',buffer_product)

def InsertTable2(product): # ใช้กับ Barcode Scanner
	# product = '1001' or Barcode ID
	global buffer_product # ทำให้สามารถแก้ไขตัวแปรภายนอกฟังก์ชั่นได้
	# product = 'espresso'
	if product not in buffer_product:
		# หากไม่มีสินค้าในรายการซื้อครั้งนี้ จะทำขั้นตอนนี้
		pdname = stockproduct[product]['pdname']
		pdprice = stockproduct[product]['pdprice']
		quan = 1
		total = quan * pdprice
		rw = [product,pdname,quan,pdprice,total]
		buffer_product[product] = rw # เก็บไว้ชั่วคราว
		try: 
			for bp in buffer_product.items():
				if bp[1][1] == 'Cash Discount':
					cdkey = bp[1][0]
					cdlist = bp[1]
			buffer_product.pop(cdkey)
			buffer_product[cdkey] = cdlist
		except:
			pass
	else:
		# หากสินค้ามีแล้ว เราจะทำการแก้ไขใหม่
		old = buffer_product[product] # เป็น List ['espresso',1,50,50]
		quan = old[2] + 1 # Index ที่ 0 คือ espresso Index ที่ 1 คือ จำนวน เท่ากับ 1 ดึงค่าเก่ามาบวกอีก 1
		newtotal = quan * old[3] # Index ที่ 2 คือ ราคา
		new = [old[0],old[1],quan,old[3],newtotal]
		buffer_product[product]= new

	### ลบข้อมูลเก่าใน Table ออก แล้วใส่ข้อมูลใหม่ที่พึ่ง Update เข้าไป ##########
	table_sales.delete(*table_sales.get_children()) # ลบข้อมูลใน Table ออกให้หมด
	for bp in buffer_product.values():
		# ดึงค่าล่าสุดจาก buffer_product เอามาเฉพาะ value เพื่อมาใส่เข้าไปใน Table
		table_sales.insert('','end',value=bp)

	SumTotal()
	total1 = []
	for k,v in buffer_product.items():
		total1.append(v[-1])
	total1 = sum(total1)
	discount = []
	for bp in buffer_product.items():
		if bp[1][1] == 'Cash Discount':
			discount.append(bp[1][-1])
	discount = -(sum(discount))
	total2 = total1 + discount
	netamount = total1
	creditpayment = int(v_creditpayment.get())
	cashpayment = netamount - creditpayment
	v_total2.set(total2)
	v_netamount.set(netamount)
	v_cashpayment.set(cashpayment)

	print('------------')
	print('Buffer Product : ',buffer_product)

############# Product ###############

####### Row 1 ###########
B1 = ttk.Button(F1LB1,text='Espresso',image=img_sales, compound='top')
B1.grid(row=0, column=0,ipadx=30)
B1.configure(command=lambda: InsertTable('b1001'))

B1 = ttk.Button(F1LB1,text='Americano',image=img_sales, compound='top')
B1.grid(row=0, column=1,ipadx=30)
B1.configure(command=lambda: InsertTable('b1002'))

B1 = ttk.Button(F1LB1,text='Mocca',image=img_sales, compound='top')
B1.grid(row=0, column=2,ipadx=30)
B1.configure(command=lambda: InsertTable('b1003'))

####### Row 2 ###########
B1 = ttk.Button(F1LB1,text='Cappuccino',image=img_sales, compound='top')
B1.grid(row=1, column=0,ipadx=30)
B1.configure(command=lambda: InsertTable('b1004'))

B1 = ttk.Button(F1LB1,text='Latte',image=img_sales, compound='top')
B1.grid(row=1, column=1,ipadx=30)
B1.configure(command=lambda: InsertTable('b1005'))

B1 = ttk.Button(F1LB1,text='Chocolate',image=img_sales, compound='top')
B1.grid(row=1, column=2,ipadx=30)
B1.configure(command=lambda: InsertTable('b1006'))

####### Row 3 ###########
B1 = ttk.Button(F1LB1,text='Caramel Macciato',image=img_sales, compound='top')
B1.grid(row=2, column=0,ipadx=15)
B1.configure(command=lambda: InsertTable('b1007'))

B1 = ttk.Button(F1LB1,text='White Chocolate',image=img_sales, compound='top')
B1.grid(row=2, column=1,ipadx=20)
B1.configure(command=lambda: InsertTable('b1008'))

B1 = ttk.Button(F1LB1,text='Hot Tea',image=img_sales, compound='top')
B1.grid(row=2, column=2,ipadx=30)
B1.configure(command=lambda: InsertTable('b1009'))

############# TABLE ###################

header = ['Id','Product','Quantity','Price','Total']
hw = [70,110,70,70,70] # Column Width in Table Sales

table_sales = ttk.Treeview(F1,height=10, column=header,show='headings')
table_sales.place(x=470,y=15)

for hd in header:
	table_sales.heading(hd,text=hd)

for hd,w in zip(header,hw):
	table_sales.column(hd,minwidth=w,width=w)

def ChangeQuantity(event=None):
	global buffer_product # ใส่ global เพื่อให้เปลี่ยนค่า buffer_product นอกฟังก์ชั่นนี้ได้
	try:
		select = table_sales.selection() # ตรวจสอบว่าเลือกรายการไหน
		data = table_sales.item(select) # เอารายการที่เลือกมาค้นหาว่า รายการนั้นมีอะไรบ้าง
		# print(data['values'])
		old = data['values'] # ได้ค่าเป็น List คือ ['Espresso', 1, 40, 40] ['1001', 'ส้ม', 1, 40, 40]
		# print('Old : ',old)

		def Change(event=None):
			vq = int(new_quantity.get()) # ดึงค่า new_quantity จากช่องกรอก e1 แล้วแปลงเป็นเลขจำนวนเต็ม
			new = [old[0],old[1],vq,old[3],vq*int(old[3])] # สร้างตารางใหม่ ที่เปลี่ยนค่าจำนวน (vq) และ Total ['Espresso', 100, 40, 4000]
			buffer_product[str(old[0])] = new

			# print(buffer_product)
			GUI2.withdraw() # ปิดหน้าต่างไปด้วย

			Update_table()
			SumTotal()
			total1 = []
			for k,v in buffer_product.items():
				total1.append(v[-1])
			total1 = sum(total1)
			discount = []
			for bp in buffer_product.items():
				if bp[1][1] == 'Cash Discount':
					discount.append(bp[1][-1])
			discount = -(sum(discount))
			total2 = total1 + discount
			netamount = total1
			creditpayment = int(v_creditpayment.get())
			cashpayment = netamount - creditpayment
			v_total2.set(total2)
			v_netamount.set(netamount)
			v_cashpayment.set(cashpayment)

		GUI2 = Toplevel() # เป็นหน้าต่างอื่นๆ ที่อยู่ภายใน GUI ของเรา ที่ไม่สามารถใช้ Tk ได้
		GUI2.geometry('200x150')
		GUI2.title('แก้ไขจำนวน')
		new_quantity = StringVar()
		e1 = ttk.Entry(GUI2,textvariable=new_quantity,font=(None,20))
		e1.pack() # ช่องสำหรับกรอกตัวเลขจำนวน ที่ต้องการเปลี่ยน
		b1 = ttk.Button(GUI2,text='Change',command=Change)
		b1.pack() # กดปุ่ม แล้วจะเรียก Function Change
		e1.bind('<Return>',Change) # เช็คว่าในช่องพิมพ์ มีการกดปุ่ม Enter หรือไม่ ถ้ามีให้เรียกฟังก์ชั่น Change
		e1.focus() # ให้ Curser ไปอยู่ที่ตำแหน่งที่ต้องการพิมพ์

		GUI2.mainloop()

	except Exception as e:
		print(e)
		messagebox.showinfo('Please Select Item','กรุณาเลือกสินค้าที่ต้องการเปลี่ยนจำนวน')

table_sales.bind('<F3>',ChangeQuantity) # กด F3 เพื่อแก้ไขจำนวน
table_sales.bind('<Double-1>',ChangeQuantity) # Double Click เพื่อแก้ไขจำนวน
#table_sales.bind('<a>',ChangeQuantity) กด a เพื่อแก้ไขจำนวน
#table_sales.bind('<Control-u>',ChangeQuantity) กด Ctrl + u เพื่อแก้ไขจำนวน

############ TOTAL RESULT #####################
L1 = ttk.Label(F1,text='Net Amount: ',font=(None,20))
L1.place(x=465,y=250)
v_total = StringVar()
v_total.set('0.00')

FTT = Frame(F1)
FTT.place(x=680,y=245)

total_result = ttk.Label(FTT,textvariable=v_total,font=(None,30,'bold'),foreground='green',width=8,anchor=E)
total_result.grid(row=0,column=0,sticky=E)

total = 0
def SumTotal():
	global total
	grandtotal = []
	for b in buffer_product.values():
		grandtotal.append(b[-1])
	total = sum(grandtotal)
	# total = total - int(v_discount.get())
	ftotal = f'{total:,.2f}'
	v_total.set(ftotal)

FBF = Frame(F1)
FBF.place(x=775,y=300)

FBS = ttk.Button(FBF,text='Submit',command=RunSendtoFirebase)
FBS.pack(ipadx=5,ipady=8)

########### Search Barcode Field #############
SF1 = Frame(F1)
SF1.place(x=25,y=200)

LPD1 = ttk.Label(SF1,text='Search Barcode',font=FONT).pack(pady=5)
v_search = StringVar()
Esearch = ttk.Entry(SF1,textvariable=v_search,font=FONT,width=30)
Esearch.pack()

def SearchBarcode(event=None):
	try:
		InsertTable2(v_search.get())
		v_search.set('')
	except:
		v_search.set('')
		v_status.set('ไม่มีสินค้าในระบบ กรุณาตรวจสอบอีกครั้ง')

Esearch.bind('<Return>',SearchBarcode)


##### Member Discount/Point Zone #####

FMB = ttk.LabelFrame(F1,text='Member Discount/Point')
FMB.place(x=15,y=290)

L = ttk.Label(FMB,text='Member ID:').grid(row=0,column=0)
v_mbsearch = StringVar()
Mbsearch = ttk.Entry(FMB,textvariable=v_mbsearch,font=FONT,width=14)
Mbsearch.grid(row=0,column=1,padx=5,pady=5)

########## Point Zone ##########
LR = ttk.Label(FMB,text='------- แต้ม --------',font=(None,14,'bold'))
LR.grid(padx=5,row=0,column=2,columnspan=2)

L = ttk.Label(FMB,text='แต้มสะสม').grid(padx=5,row=1,column=2)
v_currentpoint = StringVar()
v_currentpoint.set('0')
LR = ttk.Label(FMB,textvariable=v_currentpoint,font=(None,14,'bold'),foreground='orange',width=6,anchor=E)
LR.grid(padx=5,row=1,column=3)

L = ttk.Label(FMB,text='- แลกแต้ม').grid(padx=5,row=2,column=2)
v_usepoint = StringVar()
v_usepoint.set('0')
# Mbsearch = ttk.Entry(FMB,textvariable=v_usepoint,font=FONT)
Mbusepoint = ttk.Entry(FMB,textvariable=v_usepoint,justify='right',font=(None,14,'bold'),foreground='orange',width=6)
Mbusepoint.grid(row=2,column=3,padx=5,pady=5)

L = ttk.Label(FMB,text='+ ได้แต้ม').grid(padx=5,row=3,column=2)
v_point = StringVar()
v_point.set('0')
LR = ttk.Label(FMB,textvariable=v_point,font=(None,14,'bold'),foreground='orange',width=6,anchor=E)
LR.grid(padx=5,row=3,column=3)

L = ttk.Label(FMB,text='= แต้มคงเหลือ').grid(padx=5,row=4,column=2)
v_pointbalance = StringVar()
v_pointbalance.set('0')
LR = ttk.Label(FMB,textvariable=v_pointbalance,font=(None,14,'bold'),foreground='orange',width=6,anchor=E)
LR.grid(padx=5,row=4,column=3)

########## Credit Zone ##########
LR = ttk.Label(FMB,text='------- เครดิต --------',font=(None,14,'bold'))
LR.grid(padx=5,row=0,column=4,columnspan=2)

L = ttk.Label(FMB,text='เครดิตสะสม').grid(padx=5,row=1,column=4)
v_currentcredit = StringVar()
v_currentcredit.set('0')
LR = ttk.Label(FMB,textvariable=v_currentcredit,font=(None,14,'bold'),foreground='purple',width=6,anchor=E)
LR.grid(padx=5,row=1,column=5)

L = ttk.Label(FMB,text='+ เติมเงินเครดิต').grid(padx=5,row=2,column=4)
v_addcredit = StringVar()
v_addcredit.set('0')
Mbaddcredit = ttk.Entry(FMB,textvariable=v_addcredit,justify='right',font=(None,14,'bold',),foreground='purple',width=6)
Mbaddcredit.grid(row=2,column=5,padx=5,pady=5)

L = ttk.Label(FMB,text='- ใช้เงินเครดิต').grid(padx=5,row=3,column=4)
v_usecredit = StringVar()
v_usecredit.set('0')
Mbusecredit = ttk.Entry(FMB,textvariable=v_usecredit,justify='right',font=(None,14,'bold',),foreground='purple',width=6)
Mbusecredit.grid(row=3,column=5,padx=5,pady=5)
Mbusecredit.configure(state='disabled')

L = ttk.Label(FMB,text='= เครดิตคงเหลือ').grid(padx=5,row=4,column=4)
v_creditbalance = StringVar()
v_creditbalance.set('0')
LR = ttk.Label(FMB,textvariable=v_creditbalance,font=(None,14,'bold'),foreground='purple',width=6,anchor=E)
LR.grid(padx=5,row=4,column=5)

########## Amount & Discount Zone ##########
L = ttk.Label(FMB,text='ยอดเงินรวม (บาท)').grid(padx=5,row=0,column=6)
v_total2 = StringVar()
v_total2.set('0')
LR = ttk.Label(FMB,textvariable=v_total2,font=(None,14,'bold'),foreground='brown',width=7,anchor=E)
LR.grid(padx=5,row=0,column=7)

L = ttk.Label(FMB,text='- ส่วนลดใช้แต้ม (บาท)').grid(padx=5,row=1,column=6)
v_discount = StringVar()
v_discount.set('0')
LR = ttk.Label(FMB,textvariable=v_discount,font=(None,14,'bold'),foreground='brown',width=7,anchor=E)
LR.grid(padx=5,row=1,column=7)

L = ttk.Label(FMB,text='= ยอดเงินสุทธิ (บาท)').grid(padx=5,row=2,column=6)
v_netamount = StringVar()
v_netamount.set('0')
LR = ttk.Label(FMB,textvariable=v_netamount,font=(None,14,'bold'),foreground='brown',width=7,anchor=E)
LR.grid(padx=5,row=2,column=7)

########## Function to Insert Cash Discount in Sales Transaction #########

def InsertCashDiscount():
	global buffer_product
	global discount
	global countcdtran
	if discount > 0:
		pdid = 'D1001'
		pdname = 'Cash Discount'
		pdprice = -discount
		pdquan = 1
		total = pdquan * pdprice
		rw = [pdid,pdname,pdquan,pdprice,total]
		buffer_product[pdid] = rw 
		##### ลบข้อมูลเก่าใน Table ออก แล้วใส่ข้อมูลใหม่ที่พึ่ง Update เข้าไป #####
		table_sales.delete(*table_sales.get_children()) # ลบข้อมูลใน Table ออกให้หมด
		for bp in buffer_product.values():
			# ดึงค่าล่าสุดจาก buffer_product เอามาเฉพาะ value เพื่อมาใส่เข้าไปใน Table
			table_sales.insert('','end',value=bp)

	SumTotal()

########## Check Member Function ##########
checktel = {}
editmember2 = {}
discount = 0
checkmember = {}

def CheckMember(event=None):
	global total
	global discount
	global point_settings
	global checkmember
	mid = v_mbsearch.get()
	try:	
		member = allmember[mid]
	except:
		for ID,m in allmember.items():
			checktel[m['membertel']] = ID
		mid = allmember[checktel[mid]]
		member = mid

	membertext1 = f"คุณ: {member['membername']}"
	membertext2 = f"แต้มสะสม: {member['memberpoint']} point"
	membertext3 = f"เครดิตสะสม {member['membercredit']} บาท"
	v_memberdetail1.set(membertext1)
	v_memberdetail2.set(membertext2)
	v_memberdetail3.set(membertext3)

	addcredit = int(v_addcredit.get())
	if addcredit > 0:
		messagebox.showinfo('เติมเงินเครดิต',f'คุณลูกค้า ต้องการเติมเงินเดรดิต จำนวน {addcredit} บาท')
		newcredit = int(member['membercredit']) + addcredit
		mbidcredit = member['memberid']
		editmember2 = {'memberid': member['memberid'],'membername': member['membername'],
					'membertel': member['membertel'],'membertype': member['membertype'],
					'memberpoint': member['memberpoint'],'membercredit': str(newcredit)}
		sendmb = firebase.put('/member',mbidcredit,editmember2)
		RunUpdateMemberTable()
		membertext3 = f"เครดิตสะสม {newcredit} บาท"
		v_memberdetail3.set(membertext3)
		addcredit = 0 						# Reset ค่า addcredit ให้เป็น 0								
		v_currentcredit.set(newcredit)
		v_addcredit.set(addcredit)
		v_creditbalance.set(newcredit)
	else:
		creditnow = int(member['membercredit'])
		addcredit = 0		

		v1 = int(list(point_settings[member['membertype']].values())[0])
		v2 = int(list(point_settings[member['membertype']].values())[1])
		v3 = int(list(point_settings[member['membertype']].values())[2])
		v4 = int(list(point_settings[member['membertype']].values())[3])

		pointnow = int(member['memberpoint'])
		v_currentpoint.set(pointnow)
		# total = float(v_total.get())
		if discount > 0: # discount จากรายการ Cash Discount ใน Sales Table ต้องปรับให้ตัวเลขถูกต้องก่อน
			total = total + discount
			v_total2.set(total)
		else:
			total = total
			v_total2.set(total)
		
		if total == 0:
			messagebox.showinfo('','ขณะนี้ยังไม่มียอดซื้อ คุณลูกค้ายังไม่สามารถใช้แต้มได้')
			usepoint = 0
			v_usepoint.set(usepoint)

		usepoint = int(v_usepoint.get())
		discount = (int(usepoint) // v3) * v4
		netamount = total - discount
		v_discount.set(discount)
		v_netamount.set(netamount)

		if netamount < 0:
			getpoint = 0
			maxusepoint = (total // v4) * v3 
			discount = (maxusepoint // v3) * v4
			infotext = f'รายการซื้อครั้งนี้ ใช้แต้มได้สูงสุด {maxusepoint} แต้ม คิดเป็นส่วนลด {discount} บาท'
			messagebox.showinfo('แต้มแลกได้สูงสุด',infotext)
			usepoint = maxusepoint
			netamount = total - discount
			v_netamount.set(netamount)
			v_usepoint.set(usepoint)
			v_discount.set(discount)
			v_point.set(getpoint)
		else:
			getpoint = (netamount // v1) * v2
			v_point.set(getpoint)

		InsertCashDiscount()

		pointbalance = pointnow - usepoint + getpoint
		v_pointbalance.set(pointbalance)

		paymentmethod = v_payment.get()

		if paymentmethod == 'credit':
			usecredit = int(v_usecredit.get())
		else:
			usecredit = 0
			v_usecredit.set(usecredit)

		creditbalance = creditnow + addcredit - usecredit
		v_currentcredit.set(creditnow)
		v_creditbalance.set(creditbalance)
		creditpayment = usecredit
		cashpayment = netamount - creditpayment
		v_creditpayment.set(creditpayment)
		v_cashpayment.set(cashpayment)
		checkmember = member.copy()
		checkmember['memberpoint'] = pointbalance
		checkmember['membercredit'] = creditbalance
		
def UpdateMbPointandCredit():
	global checkember
	mbid = checkmember['memberid']
	data_update = checkmember
	try:
		update = firebase.patch('/member/'+str(mbid),data_update)
	except:
		print('Error Updating Member Point and Credit for Member ID: ', mbid)
	
	v_mbsearch.set('')
	v_memberdetail1.set('----- member -----')
	v_memberdetail2.set('----- point -----')
	v_memberdetail3.set('----- credit -----')
	v_currentpoint.set('0')
	v_usepoint.set('0')
	v_point.set('0')
	v_pointbalance.set('0')
	v_currentcredit.set('0')
	v_addcredit.set('0')
	v_usecredit.set('0')
	v_creditbalance.set('0')
	v_total2.set('0')
	v_discount.set('0')
	v_netamount.set('0')
	v_creditpayment.set('0')
	v_cashpayment.set('0')
	RB1.invoke()

	UpdateMemberTable()


########## Check Member Button ##########

Bcheck = ttk.Button(FMB,text='Check Member / Add Credit',command=CheckMember)
Bcheck.grid(padx=5,row=1,columnspan=2,ipadx=5,ipady=5)

Mbsearch.bind('<Return>',CheckMember)
# Mbpoint.bind('<Return>',CheckMember)

v_memberdetail1 = StringVar()
v_memberdetail1.set('----- member -----')
LR2 = ttk.Label(FMB,textvariable=v_memberdetail1,font=(None,12,'bold'),foreground='blue')
LR2.grid(padx=5,pady=5,row=2,columnspan=2)

v_memberdetail2 = StringVar()
v_memberdetail2.set('----- point -----')
LR3 = ttk.Label(FMB,textvariable=v_memberdetail2,font=(None,12,'bold'),foreground='blue')
LR3.grid(padx=5,pady=5,row=3,columnspan=2)

v_memberdetail3 = StringVar()
v_memberdetail3.set('----- credit -----')
LR3 = ttk.Label(FMB,textvariable=v_memberdetail3,font=(None,12,'bold'),foreground='blue')
LR3.grid(padx=5,pady=5,row=4,columnspan=2)

########## Payment Method Zone ##########

L = ttk.Label(FMB,text='- จ่ายด้วยเครดิต (บาท)').grid(padx=5,row=3,column=6)
v_creditpayment = StringVar()
v_creditpayment.set('0')
LR = ttk.Label(FMB,textvariable=v_creditpayment,font=(None,14,'bold'),foreground='brown',width=7,anchor=E)
LR.grid(padx=5,row=3,column=7)

L = ttk.Label(FMB,text='= จ่ายด้วยเงินสด (บาท)').grid(padx=5,row=4,column=6)
v_cashpayment = StringVar()
v_cashpayment.set('0')
LR = ttk.Label(FMB,textvariable=v_cashpayment,font=(None,14,'bold'),foreground='brown',width=7,anchor=E)
LR.grid(padx=5,row=4,column=7)

FPM = ttk.LabelFrame(F1,text='Payment Method')
FPM.place(x=763,y=358)

L = ttk.Label(FPM,text='วิธีจ่ายเงิน').grid(padx=5,row=0,column=0)
v_payment = StringVar()
RB1 = ttk.Radiobutton(FPM,text='เงินสด (Cash)',variable=v_payment,value='cash',
	command=lambda: Mbusecredit.configure(state='disabled'))
RB1.grid(row=1,column=0,pady=8,sticky='w')
RB1.invoke()
RB2 = ttk.Radiobutton(FPM,text='เครดิต (Credit)',variable=v_payment,value='credit',
	command=lambda: Mbusecredit.configure(state='enabled'))
RB2.grid(row=2,column=0,pady=8,sticky='w')



############# Delete Function ###############
def DeleteTableSales(event=None):
	try:
		select = table_sales.selection()
		print('SELECT ID', select)
		if len(select) == 1:
			data = table_sales.item(select)
			selectproduct = data['values'][0]
			print(selectproduct)
			del buffer_product[selectproduct.lower().replace(' ','_')]
		else:
			for sl in select:
				data = table_sales.item(sl)
				selectproduct = data['values'][0]
				print(selectproduct)
				del buffer_product[selectproduct.lower().replace(' ','_')]
			selectproduct = data['values'][0] # ดักจับ Error
		
		Update_table()
		SumTotal()
	except:
		messagebox.showerror('Selection Error','กรุณาเลือกสินค้าที่ต้องการลบ')

table_sales.bind('<Delete>',DeleteTableSales)

############## CLEAR DATA ####################

def ClearDatainTable(event=None): # เพื่อส่งข้อมูลขึ้น Firebase Server บน Internet 
	global buffer_product
	table_sales.delete(*table_sales.get_children()) # ลบข้อมูลใน Table ออกให้หมด
	v_total.set('0.00')
	#messagebox.showinfo('Done','ส่งข้อมูลสำเร็จ')
	v_status.set(f'Data in table was cleared')
	buffer_product = {}

GUI.bind('<F10>',ClearDatainTable)

############### History Tab ####################

header = ['Product','Quantity','Price','Total']
hw = [110,70,70,70] # Column Width in Table Sales

table_history = ttk.Treeview(F3,height=15)
table_history.pack() # สร้าง Object ตาราง

table_history['column'] = header

for hd in header:
	table_history.heading(hd,text=hd)

for hd,w in zip(header,hw): # ปรับความกว้าง
	table_history.column(hd,minwidth=w,width=w)

LPD1 = ttk.Label(F3,text='< กด F5 เพื่ออัพเดตประวัติการขาย >',font=FONT).pack(pady=5)

def UpdateHistory():
	table_history.delete(*table_history.get_children()) # Clear All ก่อน
	v_status.set('Updating History ...')
	data = firebase.get('/','History')
	for k,v in data.items():
		# k = 2020
		# v = {'americano': {'Americano', 1, 45, 45},..........}
		total = []
		for sk,sv in v.items():
			# sk = 'americano'
			# sv = {'Americano', 1, 45, 45}
			total.append(sv[-1])
		total = sum(total)
		# total = sum([ sv[-1] for sk,sv in v.items()])
		table_history.insert('','end',k,text=f'{k} ({total}) บาท)')
		for sv in v.values():
			#sv = ['Americano', 1, 45, 45]
			table_history.insert(k,'end',values=sv)
	v_status.set('History updated')

def updatehistory(event=None): # None ต้องใช้กับ GUI.bind
	try:
		#update History
		UpdateHistory()
	except:
		messagebox.showerror("Update Error","Can't update History")

GUI.bind('<F5>',updatehistory)

############### Add Product ##########################

FPD = Frame(F2)
FPD.place(x=50,y=20)

LPD1 = ttk.Label(FPD,text='Product ID',font=FONT).pack(pady=5)
v_pdid = StringVar()
EPD1 = ttk.Entry(FPD,textvariable=v_pdid,font=FONT,width=30)
EPD1.pack()

LPD2 = ttk.Label(FPD,text='Product',font=FONT).pack(pady=5)
v_pdname = StringVar()
EPD2 = ttk.Entry(FPD,textvariable=v_pdname,font=FONT,width=30)
EPD2.pack()

LPD3 = ttk.Label(FPD,text='Price',font=FONT).pack(pady=5)
v_pdprice = StringVar()
EPD3 = ttk.Entry(FPD,textvariable=v_pdprice,font=FONT,width=30)
EPD3.pack()

LPD4 = ttk.Label(FPD,text='Quantity',font=FONT).pack(pady=5)
v_pdquan = StringVar()
EPD4 = ttk.Entry(FPD,textvariable=v_pdquan,font=FONT,width=30)
EPD4.pack()

###### Send Product to Firebase ##################

stockproduct = {} # All product in Firebase

def UpdateProductTable(event=None):
	global stockproduct
	table_product.delete(*table_product.get_children()) # Clear All ก่อน
	allproduct = firebase.get('/','Allproduct')
	# print(allproduct)
	for v in allproduct.values():
		pdlist = list(v.values())
		pdlist[-1] = '{:,.2f}'.format(pdlist[-1])
		table_product.insert('','end',values=pdlist) # ถ้าใส่ 0 แทน 'end' จะโชว์ค่าหลังสุดก่อน
	
	stockproduct = allproduct # Update Current Product in Server
	# print('Current Stock : ',stockproduct)
	v_status.set('Product Updated')

def RunUpdateProductTable(event=None):
	v_status.set('Updating...')
	thread1 = Thread(target=UpdateProductTable) # ใช้ Thread ช่่วยในการทำงานคู่ขนานกัน
	thread1.start()

GUI.bind('<F4>',RunUpdateProductTable) # กด F4 เพื่อ Update Product Table

def SendProducttoFirebase(): # เพื่อส่งข้อมูลขึ้น Firebase Server บน Internet 
	pdid = v_pdid.get()
	pdname = v_pdname.get()
	pdprice = int(v_pdprice.get())
	pdquan = int(v_pdquan.get())
	total = int(pdprice * pdquan)
	product = {'pdid':pdid,'pdname':pdname,'pdprice':pdprice,'pdquan':pdquan,'total':total}
	send = firebase.put('/Allproduct',pdid,product)

	#messagebox.showinfo('Done','ส่งข้อมูลสำเร็จ')
	v_status.set(f'Record: {pdid} - Done!')
	v_pdid.set('')
	v_pdname.set('')
	v_pdprice.set('')
	v_pdquan.set('')

	RunUpdateProductTable()

###### Threading ##################
def RunSendProducttoFirebase():
	v_status.set('Uploading...')
	thread1 = Thread(target=SendProducttoFirebase) # ใช้ Thread ช่่วยในการทำงานคู่ขนานกัน
	thread1.start()

BPD = ttk.Button(FPD,text='Add / Edit Product',command=RunSendProducttoFirebase)
BPD.pack(ipadx=20,ipady=10,pady=10)

############### STATUS BAR ################

v_status = StringVar() # เก็บค่า status
v_status.set('This is a status bar')
statusbar = Label(GUI,textvariable=v_status,bd=1,relief=SUNKEN,anchor=W)
statusbar.pack(side=BOTTOM,fill=X)

################ Product ID and Detail ###########################

header = ['Product ID','Product','Price','Quantity','Total']
hw = [100,100,70,70,70] # Column Width in Table Sales

table_product = ttk.Treeview(F2,height=17, column=header,show='headings')
table_product.place(x=300,y=20)

for hd in header:
	table_product.heading(hd,text=hd)

for hd,w in zip(header,hw):
	table_product.column(hd,minwidth=w,width=w)

L1 = Label(F2,text='<กดปุ่ม F4 เพื่ออัพเดตรายการสินค้า>',font=('Angsana New',15)).place(x=410,y=390)
L2 = Label(F2,text='<ดับเบิลคลิกเมาส์ เพื่อแก้ไขรายการสินค้า>',font=('Angsana New',15)).place(x=400,y=420)

# LFRAME = Frame(F2)
# LFRAME.place(x=700,y=50)
# from tkinter.mywidget import * # ดึง mywidget ที่สร้างขึ้นมาเอง ใน tkinter มาใช้
# L1 = MyLabel(LFRAME,'ข้อความ1',0,0)
# L2 = MyLabel(LFRAME,'ข้อความ2',0,1,20,'red')
# L3 = MyLabel(LFRAME,'ข้อความ3',1,0,25)
# L4 = MyLabel(LFRAME,'ข้อความ4',1,1,30)

########## Edit Table Product Function ##########
def EditTableProduct(event=None):
	global stockproduct
	stockproduct = firebase.get('/','Allproduct')
	select = table_product.selection()

	try:
		if len(select) == 1:
			data = table_product.item(select)
			selectproduct = str(data['values'][0])

			v_pdid.set(stockproduct[selectproduct]['pdid'])
			v_pdname.set(stockproduct[selectproduct]['pdname'])
			v_pdprice.set(int(stockproduct[selectproduct]['pdprice']))
			v_pdquan.set(int(stockproduct[selectproduct]['pdquan']))

		else:
			messagebox.showerror('Select Error','กรุณาเลือกสินค้าที่ต้องการแก้ไขเพียงรายการเดียว')

	except:
		messagebox.showerror('Select Error','กรุณาเลือกสินค้าที่ต้องการแก้ไข')

table_product.bind('<Double-1>',EditTableProduct) # กดปุ่ม Delete เพื่อลบรายการสมาชิกที่เลือกใน Member Table


########## Delete Table Product Function ##########
def DeleteTableProduct(event=None):
	global stockproduct
	stockproduct = firebase.get('/','Allproduct')
	select = table_product.selection()

	try:
		if len(select) == 1:
			data = table_product.item(select)
			selectproduct = data['values'][0]
			del stockproduct[str(selectproduct)]
			deletepd = firebase.delete('/Allproduct',str(selectproduct)) # ลบรายการสมาชิกใน Firebase
		else:
			for sl in select:
				data = table_product.item(sl)
				selectproduct = data['values'][0]
				del stockproduct[str(selectproduct)]
				deletepd = firebase.delete('/Allproduct',str(selectproduct))
			selectproduct = data['values'][0] # ดักจับ Error
		
		RunUpdateProductTable()

	except:
		messagebox.showerror('Selection Error','กรุณาเลือกสินค้าที่ต้องการลบ')

table_product.bind('<Delete>',DeleteTableProduct) # กดปุ่ม Delete เพื่อลบรายการสมาชิกที่เลือกใน Member Table

########## Clear Table Product Function ##########
def ClearTableProduct(event=None): # เพื่อส่งข้อมูลขึ้น Firebase Server บน Internet 
	global stockproduct
	table_product.delete(*table_product.get_children()) # ลบข้อมูลใน Table ออกให้หมด
	#messagebox.showinfo('Done','ส่งข้อมูลสำเร็จ')
	v_status.set(f'Data in product table was cleared')
	stockproduct = {}

GUI.bind('<F12>',ClearTableProduct) # กดปุ่ม F12 เพื่อลบทุกรายการใน Product Table

############# Member ##################
# allmember = {'M001':{'mid':'M1001','name':'Somchai',
# 			'tel':'081234','membertype':'Silver','point':500,'credit':100},
#			'M1002':{'mid':'M1002','name':'Somsak',
#			'tel':'081234','membertype':'Silver','point':500,'credit':100},}


################################################
#                 ALL MEMBER DATA IN PROGRAM
####################### member ##################
allmember = {}

Tabmember = Notebook(F4)
F41 = Frame()
F42 = Frame()
F43 = Frame()
Tabmember.add(F41,text='member')
Tabmember.add(F42,text='add members')
Tabmember.add(F43,text='settings')
Tabmember.pack(fill=BOTH,expand=1,padx=20,pady=10)

##### member #####

def SearchMember(event=None):
	search = v_searchmember.get()
	try:
		try: 
			result = allmember[search]
		except:
			result = allmember[checktel[search]]

		ve_memberid.set(result['memberid'])
		ve_membername.set(result['membername'])
		ve_membertel.set(result['membertel'])
		CBE.set(result['membertype'])
		ve_memberpoint.set(result['memberpoint'])
		ve_membercredit.set(result['membercredit'])

	except:
		print('No Result')
		messagebox.showwarning('ไม่มีรหัสผุ้ใช้',f'รหัส {search} ไม่มีในระบบ')


FMS = Frame(F41)
FMS.place(x=50,y=10)

L1 = ttk.Label(FMS,text='Search [ID/Tel]').grid(row=0,column=0)
v_searchmember = StringVar()
Searchmember = ttk.Entry(FMS,textvariable=v_searchmember,font=FONT,width=35)
Searchmember.grid(row=0,column=1,padx=3,pady=20)

Searchmember.bind('<Return>',SearchMember)

BS = ttk.Button(FMS,text='Search',command=SearchMember)
BS.grid(row=0,column=2,pady=10,padx=20,ipadx=20,ipady=8)

FM1 = Frame(F41)
FM1.place(x=50,y=80)

L1 = ttk.Label(FM1,text='Member ID').grid(row=0,column=0)
ve_memberid = StringVar()
EM1 = ttk.Entry(FM1,textvariable=ve_memberid,font=FONT)
EM1.grid(row=0,column=1)

L2 = ttk.Label(FM1,text='Name').grid(row=1,column=0)
ve_membername = StringVar()
EM2 = ttk.Entry(FM1,textvariable=ve_membername,font=FONT)
EM2.grid(row=1,column=1,pady=10,padx=20)

L3 = ttk.Label(FM1,text='Tel').grid(row=2,column=0)
ve_membertel = StringVar()
EM3 = ttk.Entry(FM1,textvariable=ve_membertel,font=FONT)
EM3.grid(row=2,column=1,pady=10,padx=20)

L4 = ttk.Label(FM1,text='Member Type').grid(row=0,column=2)
CBE = ttk.Combobox(FM1, values=['Platinum','Gold','Silver'],font=FONT,width=18)
CBE.set('Silver')
CBE.grid(row=0,column=3,pady=10,padx=20)

L5 = ttk.Label(FM1,text='Point').grid(row=1,column=2)
ve_memberpoint = StringVar()
ve_memberpoint.set(100)
EM5 = ttk.Entry(FM1,textvariable=ve_memberpoint,font=FONT)
EM5.grid(row=1,column=3,pady=10,padx=20)

L6 = ttk.Label(FM1,text='Credit').grid(row=2,column=2)
ve_membercredit = StringVar()
ve_membercredit.set(20)
EM6 = ttk.Entry(FM1,textvariable=ve_membercredit,font=FONT)
EM6.grid(row=2,column=3,pady=10,padx=20)

EM1.configure(state='disabled')
EM2.configure(state='disabled')
EM3.configure(state='disabled')
CBE.configure(state='disabled')
EM5.configure(state='disabled')
EM6.configure(state='disabled')

global state_editmember
state_editmember = False

def EditMember(event=None):
#	EM1.configure(state='enabled')
	global state_editmember
	global allmember
	if state_editmember == False:
#		print('enabled')
		EM2.configure(state='enabled')
		EM3.configure(state='enabled')
		CBE.configure(state='enabled')
		EM5.configure(state='enabled')
		EM6.configure(state='enabled')
		state_editmember = True
	else:
#		print('edit profile')
		allmember[ve_memberid.get()]['membername'] = ve_membername.get()
		allmember[ve_memberid.get()]['membertel'] = ve_membertel.get()
		allmember[ve_memberid.get()]['membertype'] = CBE.get()
		allmember[ve_memberid.get()]['memberpoint'] = ve_memberpoint.get()
		allmember[ve_memberid.get()]['membercredit'] = ve_membercredit.get()
		state_editmember = False
		EM1.configure(state='disabled')
		EM2.configure(state='disabled')
		EM3.configure(state='disabled')
		CBE.configure(state='disabled')
		EM5.configure(state='disabled')
		EM6.configure(state='disabled')
		firebase.put('/member',ve_memberid.get(),allmember[ve_memberid.get()])
		RunUpdateMemberTable()

Searchmember.bind('<F2>',EditMember)
EM1.bind('<F2>',EditMember)
EM2.bind('<F2>',EditMember)
EM3.bind('<F2>',EditMember)
CBE.bind('<F2>',EditMember)
EM5.bind('<F2>',EditMember)
EM6.bind('<F2>',EditMember)
Searchmember.bind('<F5>',lambda x: (EM6.configure(state='enabled'),EM6.focus()))

##### add member #####



def UpdateMemberTable(event=None):
	global allmember
	global checktel

	table_member.delete(*table_member.get_children()) # Clear All ก่อน
	members = firebase.get('/','member')
	allmember = members

	for ID,m in allmember.items():
		checktel[m['membertel']] = ID

	for v in allmember.values():
		mlist = [v['memberid'],v['membername'],
		v['membertel'],v['membertype'],v['memberpoint'],v['membercredit'],]
		table_member.insert('','end',values=mlist)
	# print('Current Member : ',allmember)
	dt = datetime.now().strftime('%H:%M:%S')
	v_status.set('อัพเดตสมาชิกใหม่แล้ว ' + dt)

def RunUpdateMemberTable(event=None):
	v_status.set('กำลังอัพเดตรายชื่อสมาชิก...')
	thread1 = Thread(target=UpdateMemberTable) # ใช้ Thread ช่่วยในการทำงานคู่ขนานกัน
	thread1.start()


def SendMembertoFirebase():
	memberid = v_memberid.get()
	membername = v_membername.get()
	membertel = v_membertel.get()
	membertype = CB1.get()
	memberpoint = int(v_memberpoint.get())
	membercredit = int(v_membercredit.get())
	member = {'memberid':memberid,
				'membername':membername,
				'membertel':membertel,
				'membertype':membertype,
				'memberpoint':memberpoint,
				'membercredit':membercredit}
	v_memberid.set('')
	v_membername.set('')
	v_membertel.set('')
	CB1.set('Silver')
	v_memberpoint.set('')
	v_membercredit.set('')
	send = firebase.put('/member',memberid,member)
	print(send)
	v_status.set(f'บันทึกผู้ใช้: {memberid} - เรียบร้อยแล้ว!')
	RunUpdateMemberTable()

def RunSendMembertoFirebase():
	v_status.set('Uploading...')
	thread1 = Thread(target=SendMembertoFirebase) # ใช้ Thread ช่่วยในการทำงานคู่ขนานกัน
	thread1.start()

#######################
FAM1 = Frame(F42)
FAM1.place(x=50,y=20)

L1 = ttk.Label(FAM1,text='Member ID').grid(row=0,column=0)
v_memberid = StringVar() #.set .get
E1 = ttk.Entry(FAM1,textvariable=v_memberid,font=FONT)
E1.grid(row=0,column=1)

L2 = ttk.Label(FAM1,text='Name').grid(row=1,column=0)
v_membername = StringVar()
E2 = ttk.Entry(FAM1,textvariable=v_membername,font=FONT)
E2.grid(row=1,column=1,pady=10,padx=20)

L3 = ttk.Label(FAM1,text='Tel').grid(row=2,column=0)
v_membertel = StringVar()
E3 = ttk.Entry(FAM1,textvariable=v_membertel,font=FONT)
E3.grid(row=2,column=1,pady=10,padx=20)

L4 = ttk.Label(FAM1,text='Member Type').grid(row=0,column=2)
CB1 = ttk.Combobox(FAM1, values=['Platimum','Gold','Silver'],font=FONT,width=18)
CB1.set('Silver')
CB1.grid(row=0,column=3,pady=10,padx=20)

L5 = ttk.Label(FAM1,text='Point').grid(row=1,column=2)
v_memberpoint = StringVar()
E5 = ttk.Entry(FAM1,textvariable=v_memberpoint,font=FONT)
E5.grid(row=1,column=3,pady=10,padx=20)

L6 = ttk.Label(FAM1,text='Credit').grid(row=2,column=2)
v_membercredit = StringVar()
E6 = ttk.Entry(FAM1,textvariable=v_membercredit,font=FONT)
E6.grid(row=2,column=3,pady=10,padx=20)

BF1 = Frame(F42)
BF1.place(x=280,y=180)

B1 = ttk.Button(BF1,text='Add Member',command=SendMembertoFirebase)
B1.pack(ipadx=20,ipady=10)

##### Member Table #####
header = ['Member ID','Name','Tel','Member Type','Point','Credit']
hw = [100,100,70,100,50,70] # Column Width in Table Member

table_member = ttk.Treeview(F42,height=17, column=header,show='headings')
table_member.place(x=50,y=260)

for hd in header:
	table_member.heading(hd,text=hd)

for hd,w in zip(header,hw):
	table_member.column(hd,minwidth=w,width=w)

L7 = Label(F42,text='<กดปุ่ม F11 เพื่ออัพเดตรายการสมาชิก>',font=('Angsana New',15)).place(x=165,y=225)

RunUpdateMemberTable()
GUI.bind('<F11>',RunUpdateMemberTable) # กด F11 เพื่อ Update Member Table


def DeleteMember(event=None):
	try:
		select = table_member.selection()
		print('select member ID',select)
		if len(select) < 2:
			data = table_member.item(select)
			selectmember = data['values'][0] # ดักจับ Error

		if len(select) == 1:
			data = table_member.item(select)
			selectmember = data['values'][0]
			print('Select member : ',selectmember)
			check = messagebox.askyesno('ขอยืนยันคำตอบ',f'คุณกำลังจะลบสมาชิกรหัส: {selectmember}\n ยืนยันกด Yes ยกเลิกกด No')
			print('Yes/No',check)
			if check == True:
				delete = firebase.delete('member/',selectmember)
				v_status.set(f'ลบสมาชิกรหัส: {selectmember} แล้ว')
				RunUpdateMemberTable()

		else:
			selectmembers = ''
			mlist = []
			for sl in select:
				data = table_member.item(sl)
				selectmember = data['values'][0]
				print('Select member : ',selectmember)
				mlist.append(selectmember)
				selectmembers += selectmember + ' ' ## **

			check = messagebox.askyesno('ขอยืนยันคำตอบ',f'คุณกำลังจะลบสมาชิกรหัส: {selectmembers}\n ยืนยันกด Yes ยกเลิกกด No')
			print('Yes/No',check)
			if check == True:
				for m in mlist:
					delete = firebase.delete('member/',m)
				
				v_status.set(f'ลบสมาชิกรหัส: {selectmember} แล้ว')
				RunUpdateMemberTable()

	except:
		messagebox.showerror('Selection Error','กรุณาเลือกสมาชิกที่ต้องการลบ')

table_member.bind('<Delete>',DeleteMember)

##### settings #####

# point_settings = {'Silver':{'silver1':100,'silver2':25,'silver3':100,'silver4':5},
# 					'Gold':{'gold1':100,'gold2':30,'gold3':100,'gold4':10},
# 					'Platinum':{'platinum1':100,'platinum2':40,'platinum3':100,'platinum4':15},
#					}

###### Silver #####

Fsilver = ttk.LabelFrame(F43,text='Silver Member')
Fsilver.place(x=50,y=20)

###### Line 1 ######
L = ttk.Label(Fsilver,text='ทุก',font=FONT).grid(row=0,column=0,padx=10,pady=10)
v_siler1 = StringVar()
E1 = ttk.Entry(Fsilver,textvariable=v_siler1,font=FONT,width=5).grid(row=0,column=1)
L = ttk.Label(Fsilver,text='บาท ลูกค้าได้รับแต้ม',font=FONT).grid(row=0,column=2,padx=10,pady=10)
v_siler2 = StringVar()
E2 = ttk.Entry(Fsilver,textvariable=v_siler2,font=FONT,width=5).grid(row=0,column=3)
L = ttk.Label(Fsilver,text='Points',font=FONT).grid(row=0,column=4,padx=10,pady=10)

###### Line 2 ######
L = ttk.Label(Fsilver,text='แลก',font=FONT).grid(row=1,column=0,padx=10,pady=10)
v_siler3 = StringVar()
E1 = ttk.Entry(Fsilver,textvariable=v_siler3,font=FONT,width=5).grid(row=1,column=1)
L = ttk.Label(Fsilver,text='Points ลูกค้าได้รับส่วนลด',font=FONT).grid(row=1,column=2,padx=10,pady=10)
v_siler4 = StringVar()
E2 = ttk.Entry(Fsilver,textvariable=v_siler4,font=FONT,width=5).grid(row=1,column=3)
L = ttk.Label(Fsilver,text='บาท',font=FONT).grid(row=1,column=4,padx=10,pady=10)

###### Gold #####

Fgold = ttk.LabelFrame(F43,text='Gold Member')
Fgold.place(x=50,y=150)

###### Line 1 ######
L = ttk.Label(Fgold,text='ทุก',font=FONT).grid(row=0,column=0,padx=10,pady=10)
v_gold1 = StringVar()
E1 = ttk.Entry(Fgold,textvariable=v_gold1,font=FONT,width=5).grid(row=0,column=1)
L = ttk.Label(Fgold,text='บาท ลูกค้าได้รับคะแนนสะสม',font=FONT).grid(row=0,column=2,padx=10,pady=10)
v_gold2 = StringVar()
E2 = ttk.Entry(Fgold,textvariable=v_gold2,font=FONT,width=5).grid(row=0,column=3)
L = ttk.Label(Fgold,text='Points',font=FONT).grid(row=0,column=4,padx=10,pady=10)

###### Line 2 ######
L = ttk.Label(Fgold,text='แลก',font=FONT).grid(row=1,column=0,padx=10,pady=10)
v_gold3 = StringVar()
E1 = ttk.Entry(Fgold,textvariable=v_gold3,font=FONT,width=5).grid(row=1,column=1)
L = ttk.Label(Fgold,text='Points ลูกค้าได้รับส่วนลด',font=FONT).grid(row=1,column=2,padx=10,pady=10)
v_gold4 = StringVar()
E2 = ttk.Entry(Fgold,textvariable=v_gold4,font=FONT,width=5).grid(row=1,column=3)
L = ttk.Label(Fgold,text='บาท',font=FONT).grid(row=1,column=4,padx=10,pady=10)

###### Platinum #####

Fplatinum = ttk.LabelFrame(F43,text='Platinum Member')
Fplatinum.place(x=50,y=280)

###### Line 1 ######
L = ttk.Label(Fplatinum,text='ทุก',font=FONT).grid(row=0,column=0,padx=10,pady=10)
v_platinum1 = StringVar()
E1 = ttk.Entry(Fplatinum,textvariable=v_platinum1,font=FONT,width=5).grid(row=0,column=1)
L = ttk.Label(Fplatinum,text='บาท ลูกค้าได้รับคะแนนสะสม',font=FONT).grid(row=0,column=2,padx=10,pady=10)
v_platinum2 = StringVar()
E2 = ttk.Entry(Fplatinum,textvariable=v_platinum2,font=FONT,width=5).grid(row=0,column=3)
L = ttk.Label(Fplatinum,text='Points',font=FONT).grid(row=0,column=4,padx=10,pady=10)

###### Line 2 ######
L = ttk.Label(Fplatinum,text='แลก',font=FONT).grid(row=1,column=0,padx=10,pady=10)
v_platinum3 = StringVar()
E1 = ttk.Entry(Fplatinum,textvariable=v_platinum3,font=FONT,width=5).grid(row=1,column=1)
L = ttk.Label(Fplatinum,text='Points ลูกค้าได้รับส่วนลด',font=FONT).grid(row=1,column=2,padx=10,pady=10)
v_platinum4 = StringVar()
E2 = ttk.Entry(Fplatinum,textvariable=v_platinum4,font=FONT,width=5).grid(row=1,column=3)
L = ttk.Label(Fplatinum,text='บาท',font=FONT).grid(row=1,column=4,padx=10,pady=10)

point_settings = {}

def UpdatePointSettings(event=None):
	global point_settings

	point_settings = firebase.get('/','point')

	v_siler1.set(point_settings['Silver']['silver1'])
	v_siler2.set(point_settings['Silver']['silver2'])
	v_siler3.set(point_settings['Silver']['silver3'])
	v_siler4.set(point_settings['Silver']['silver4'])

	v_gold1.set(point_settings['Gold']['gold1'])
	v_gold2.set(point_settings['Gold']['gold2'])
	v_gold3.set(point_settings['Gold']['gold3'])
	v_gold4.set(point_settings['Gold']['gold4'])

	v_platinum1.set(point_settings['Platinum']['platinum1'])
	v_platinum2.set(point_settings['Platinum']['platinum2'])
	v_platinum3.set(point_settings['Platinum']['platinum3'])
	v_platinum4.set(point_settings['Platinum']['platinum4'])

	v_status.set(f'อัพเดตแต้ม Silver, Gold, Platinum เรียบร้อยแล้ว')

def RunUpdatePointSettings(event=None):
	v_status.set('กำลังอัพเดตแต้ม Silver, Gold, Platinum ...')
	thread1 = Thread(target=UpdatePointSettings)
	thread1.start()

def SendPointSettingstoFirebase():
	s1 = v_siler1.get()
	s2 = v_siler2.get()
	s3 = v_siler3.get()
	s4 = v_siler4.get()
	g1 = v_gold1.get()
	g2 = v_gold2.get()
	g3 = v_gold3.get()
	g4 = v_gold4.get()
	p1 = v_platinum1.get()
	p2 = v_platinum2.get()
	p3 = v_platinum3.get()
	p4 = v_platinum4.get()

	data = {'Silver':{'silver1':s1,'silver2':s2,'silver3':s3,'silver4':s4},
					'Gold':{'gold1':g1,'gold2':g2,'gold3':g3,'gold4':g4},
					'Platinum':{'platinum1':p1,'platinum2':p2,'platinum3':p3,'platinum4':p4},
					}
	for k,v in data.items():	
		send = firebase.put('/point',k,v)

	v_status.set(f'บันทึกแต้ม Silver, Gold, Platinum เรียบร้อยแล้ว')
	RunUpdatePointSettings()

def RunSendPointSettingstoFirebase():
	v_status.set('Uploading...')
	thread1 = Thread(target=SendPointSettingstoFirebase)
	thread1.start()

########## Button to Save Settings ##########

BSF = Frame(F43)
BSF.place(x=150,y=414)

BS1 = ttk.Button(BSF,text='Save Settings',command=RunSendPointSettingstoFirebase)
BS1.pack(ipadx=20,ipady=10)

################ Start up ##################
try:
	RunUpdateProductTable()
	RunUpdatePointSettings()
except:
	messagebox.showerror('Stock Error','ไม่สามารถซิ้งค์ข้อมูลกับเซอร์เวอร์ได้')

GUI.mainloop()