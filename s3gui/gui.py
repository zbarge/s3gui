# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 21:29:18 2016

@author: Zeke
"""
import os
import json
from s3 import S3Client
from tkinter import LEFT, RIGHT, TOP, BOTTOM, END, Tk, Listbox, Menu, filedialog
from tkinter.ttk import Entry, Frame, Label, Button, Treeview, Scrollbar
SETTINGS = {'ROOT_DIR':'C:/Users/Zeke/Google Drive/dev/python/bakker/bakker/data',
            'SETTINGS_FILENAME':'settings.txt',
            '':'',
            }

        
class AwsUploader(Frame):
    
    def __init__(self, master=None, settings=None):
        """
        settings:
            ROOT_DIR: (str) path to directory for root of app
            SETTINGS_FILENAME: the name of the settings file
        
        """
        self.aws = S3Client()
        master.title("AWS Manager")
        self.settings = (settings if settings is not None else {})
        
        if settings:
            self.save_settings()
            
        Frame.__init__(self, master)
        self.grid()
        self.create_widgets()
        
    @property
    def root_dir(self):
        return self.settings['ROOT_DIR']
        
    @property
    def settings_path(self):
        return os.path.join(self.root_dir, 
                            self.settings['SETTINGS_FILENAME'])
    
    def read_settings(self):
        if os.path.exists(self.settings_path):
            
            with open(self.settings_path, "r") as fp:
                try:
                    
                    settings = json.load(fp)
                    
                except Exception as e:
                    #Issue parsing the settings file.
                    print(e)
                    settings = self.settings.copy()
                    
        else:
            settings = self.settings.copy()
            
        return settings
        
    def save_settings(self):
        settings = self.settings.copy()
        current_settings = self.read_settings()
        current_settings.update(settings)
        if not os.path.exists(self.root_dir):
            os.mkdir(self.root_dir)
        with open(self.settings_path, "w") as fp:
            json.dump(current_settings, fp)
            
        self.settings = current_settings
        
        return self.settings
        
        
    def create_widgets(self):
        
        #Store menu items
        self.FILE_MENU = Menu(self)
        self.FILE_MENU.add_command(label="Quit", command=self.quit)
        self.FILE_MENU.add_command(label="Save", command=self.save_settings)
        self.FILE_MENU.add_command(label="Refresh", command=self.create_widgets)
        self.FILE_MENU.add_command(label="Open", command=self.open_bucket)
        self.FILE_MENU.add_command(label="Create", command=self.create_bucket)
        self.FILE_MENU.add_command(label="Delete", command=self.delete_bucket_item)
        self.FILE_MENU.add_command(label="Upload", command=self.upload_file)
        self.FILE_MENU.add_command(label="Upload Dirs", command=self.upload_directory)
        self.FILE_MENU.add_command(label="Sync Dir", command=self.sync_directory)
        self.master.config(menu=self.FILE_MENU)

        
        #Store credentials
        #If none in environment
        self.LABEL_KEY = Label(self, text="AWS Key:")
        self.LABEL_KEY.grid(row=0,column=0)
        
        self.ENTRY_KEY = Entry(self)
        self.ENTRY_KEY.grid(row=0,column=1)
        
        self.LABEL_SECRET = Label(self, text="AWS Secret:")
        self.LABEL_SECRET.grid(row=1,column=0)
        
        self.ENTRY_SECRET = Entry(self, show=False)
        self.ENTRY_SECRET.grid(row=1,column=1)
        
        
        self.LABEL_NEW_BUCKET = Label(self, text="Bucket Name:")
        self.LABEL_NEW_BUCKET.grid(row=2,column=0)
        
        self.ENTRY_NEW_BUCKET = Entry(self)
        self.ENTRY_NEW_BUCKET.grid(row=2,column=1)
        
        #The bucket tree will contain 
        #S3 files/directores.        
        self.BUCKET_TREE = Treeview(self, 
                                    columns=('Bucket', 'Key', 'Modified'),
                                    selectmode='extended',)
        
        ysb = Scrollbar(self, orient='vertical', command=self.BUCKET_TREE.yview)
        xsb = Scrollbar(self, orient='horizontal', command=self.BUCKET_TREE.xview)
        self.BUCKET_TREE.configure(yscroll=ysb.set, xscroll=xsb.set)
        
        self.BUCKET_TREE.heading("#0", text="Item ID")
        self.BUCKET_TREE.heading("#1", text="Bucket")
        self.BUCKET_TREE.heading("#2", text="Key")
        self.BUCKET_TREE.heading("#3", text="Modified")
        
        self.BUCKET_TREE.column(0, minwidth=100,)
        
        #Load top level S3 directories
        #into the bucket tree
        count = 0
        for bucket in self.aws.s3.buckets.all():
            self.BUCKET_TREE.insert('', END, count, 
                                    text=count, 
                                    values=(bucket.name, 
                                            bucket.name, 
                                            None, 
                                            bucket.name))
            count += 1
                
        self.BUCKET_TREE.grid(row=4,column=0, columnspan=5)
        ysb.grid(row=4, column=5, sticky='ns')
        xsb.grid(row=5, column=0, columnspan=5, sticky='ew')    
        
    def open_bucket(self):
        """
        Inserts all objects
        associated with the selected
        bucket as children into
        the treeview.
        """
        idx = self.BUCKET_TREE.focus()
        if not idx:
            return None
            
        item = self.BUCKET_TREE.item(idx)
        children = self.BUCKET_TREE.get_children(idx)
        
        if children:
            self.BUCKET_TREE.delete(*children)
            
        bucket_name =   item['values'][0]  
        bucket = self.aws.s3.Bucket(bucket_name)
        
        count = 0
        folders = {}
                   
        for obj in bucket.objects.all():
            
            child_idx = "{}_{}".format(bucket.name, count)
            
            prefix_dirname = self.aws.get_prefix_dirname(obj.key)
            
            try:
                parent_idx = folders[prefix_dirname]
            except KeyError:
                #Assign new top level for directory
                folders[prefix_dirname] = child_idx
                
                parts = prefix_dirname.split("/")
                parent_prefix = "/".join(parts[:-1])
                
                try:
                    #Get another chld for parent
                    parent_idx = folders[parent_prefix]
                    
                except KeyError:
                    #Use top level bucket as parent
                    #As last resort.
                    parent_idx = idx
                 
            self.BUCKET_TREE.insert(parent_idx, 
                                    END, 
                                    child_idx, 
                                    text=child_idx, 
                                    values=(bucket.name, 
                                            obj.key, 
                                            None, 
                                            prefix_dirname))
            count += 1
            
    def delete_bucket_item(self):
        """
        Deletes a bucket or bucket item from AWS
        Then removes the item from the Treeview
        AWS will kick an error if you try
        to delete a non-empty bucket.
        """
        idx = self.BUCKET_TREE.focus()
        if not idx:
            return None
        item = self.BUCKET_TREE.item(idx)
        
        children = self.BUCKET_TREE.get_children(idx)
        if children:
            #Dont delete (yet)
            #TODO: count children and confirm Y/N
            print("Skipping delete of bucket {} because it has children".format(item))
            pass
        else:
            
            bucket_name = item['values'][0]
            bucket_prefix = item['values'][1]
            bucket = self.aws.s3.Bucket(bucket_name)
            print("Deleting {}".format(item))          
            if bucket_name == bucket_prefix:
                #This is a top level bucket
                bucket.delete()
            else:
                #This is a child object of a bucket.

                objs = bucket.objects.filter(Prefix=bucket_prefix)
                for obj in objs:
                    obj.delete()
            self.BUCKET_TREE.delete(idx)
            
    def create_bucket(self):
        new_name = self.ENTRY_NEW_BUCKET.get()
        if new_name:
            print("Creating bucket: {}".format(new_name))
            self.aws.client.create_bucket(Bucket=new_name)
            self.create_widgets()
        
    def upload_file(self, file_path=None, idx=None):
        if file_path is None:
            file_path = filedialog.askopenfilename(filetypes = (("All files", "*.*")
                                                  ,("HTML files", "*.html;*.htm")
                                                  ))
        file_name = os.path.basename(file_path)
        
        if not idx:
            idx = self.BUCKET_TREE.focus()
            
        if not idx:
            return None
        item = self.BUCKET_TREE.item(idx)
        
        bucket_name = item['values'][0]
        bucket_prefix = item['values'][1]
        if bucket_name == bucket_prefix:
            #upload file to bucket directly
            bucket_prefix = file_name
        else:
            #A file or dirname is selected, check for prefix
            #Getthe prefix dirname
            bp = item['values'][3]
                
            if not bp[-1] == "/":
                bp += "/"
            
            bucket_prefix = bp + file_name
        print("Uploading {} to {}".format(file_path, bucket_prefix))    
        self.aws.client.upload_file(file_path, bucket_name, bucket_prefix)
        self.create_widgets()
        
    def upload_directory(self, dir_path=None, idx=None):
        """
        Recreates a directory
        into an AWS bucket.
        """
        if dir_path is None:
            dir_path = filedialog.askdirectory()
        dir_path = os.path.normpath(dir_path).replace('\\','/')
        parent_dir = os.path.dirname(dir_path).replace('\\','/')
        
        if idx is None:
            idx = self.BUCKET_TREE.focus()
            
        if not idx:
            return None
        item = self.BUCKET_TREE.item(idx)
        
        bucket_name = item['values'][0]
        parent_prefix = item['values'][1]
        if bucket_name == parent_prefix:
            parent_prefix = ""
            
        for dirname, subdirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.normpath(os.path.join(dirname, file)).replace('\\','/')
                bucket_prefix = os.path.dirname(file_path).replace(parent_dir, "/").replace('//','/')
                
                if not bucket_prefix.endswith('/'):
                    bucket_prefix += "/"
                    
                bucket_prefix = parent_prefix + bucket_prefix + file
                
                print("Uploading {} to {}".format(bucket_prefix, bucket_name))    
                self.aws.client.upload_file(file_path, bucket_name, bucket_prefix)
        self.create_widgets()
        
    def sync_directory(self, dir_path=None, idx=None):
        refresh = False
        if dir_path is None:
            dir_path = filedialog.askdirectory()
            refresh = True
            
        if idx is None:
            idx = self.BUCKET_TREE.focus()
            
        if not idx:
            return None
        
        item = self.BUCKET_TREE.item(idx)
        
        bucket_name = item['values'][0]
        bucket_prefix = item['values'][3]
        if bucket_prefix == bucket_name:
            bucket_prefix = None
            
        self.aws.sync_directory(dir_path, bucket_name, key_name=bucket_prefix,)
        
        if refresh:
            self.create_widgets()
        
        

def main():
    root = Tk()
    
    try:
        
        app = AwsUploader(master=root, settings=SETTINGS)
        app.mainloop()
        
    
    finally:
        
        try:
            
            root.destroy()
            
        except:
            pass        
 
if __name__ == '__main__':
    

    main()
       

