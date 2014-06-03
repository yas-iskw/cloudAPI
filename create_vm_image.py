#coding: utf-8
import libvirt
import sys
import os
import re
import uuid
import xml.etree.ElementTree as ET


class VmManager(object):
    def __init__(self):
        self.conn = libvirt.open('qemu:///system')
        self.xml_templete = "./templete.xml"
        self.default_mem_size = "256"
        self.default_cpu_size = "1"
        self.default_source_iso = "debian-7.5.0-amd64-netinst.iso"

    def deleteByName(self, vm_name):
        vm = self.conn.lookupByID(vm_name)
        self.vm.undefine()

    def createByName(self, vm_name, hd_size, mem_size, cpu_size):
        self.__create_image(vm_name, hd_size)
        parser = ParseXml(self.xml_templete, vm_name, mem_size, cpu_size, self.default_source_iso)
        parser.create_new_xml()
        os.system("virsh define %s" % vm_name + '.xml')

    def __create_image(self,vm_name,hd_size):
        os.system("qemu-img create -f qcow2 /var/lib/libvirt/images/%s.img %sG" % (vm_name, hd_size))

    def getVMByName(self, vm_name):
        try:
            vm = self.conn.lookupByName(vm_name)
        except:
            print 'Failed to lookup'
            sys.exit(1)
        return vm

        
    def startByName(self, vm_name):
        vm = self.getVMByName(vm_name)
        #print 'start : ' + name
        vm.create()

    def shutdownByName(self, vm_name):
        vm = self.getVMByName(vm_name)
        #print 'shutdown : ' + name
        vm.shutdown()
        vm.destroy()
        
    def startAllVM(self):
        for name in self.getShutoffVMListName():
            self.startByName(name)

    def shutdownAllVM(self):
        for name in self.getRunningVMListName():
            self.shutdownByName(name)

    def getALLVMStatus(self):
        for name in self.getVMNameList():
            self.getVMStatusByName(name)


        
class ParseXml(object):
    def __init__(self, filename, vm_name, mem_size, cpu_size, source_name):
        self.filename = filename
        self.tree = ET.parse(filename)
        self.root = self.tree.getroot()
        self.vm_name = vm_name
        self.mem_size = mem_size
        self.cpu_size = cpu_size
        self.source_name = source_name

    def set_image_name(self):
        disk = self.tree.find('./devices/disk')
        if disk.get('device') == 'disk':
            image = disk.find('./source')
            image.set('file', '/var/lib/libvirt/images/' + self.vm_name + '.img')

    def set_name(self):
        name = self.tree.find('./name')
        name.text = self.vm_name

    def set_uuid(self):
        new_uuid = uuid.uuid4()
        uuid_node = self.tree.find('./uuid')
        uuid_node.text = str(new_uuid)
            
    def set_mem_size(self):
        mem = self.tree.find('./memory')
        mem.text = str(int(self.mem_size)*1024)
        curmem = self.tree.find('./currentMemory')
        curmem.text = str(int(self.mem_size)*1024)

    def set_cpu_size(self):
        cpu = self.tree.find('./vcpu')
        cpu.text = self.cpu_size

    def set_source_name(self):
        for disk in self.tree.findall('./devices/disk'):
            if disk.get('device') == 'cdrom':
                source = disk.find('./source')
                source.set('file', '/var/isoimages/' + self.source_name)

    def write_xml(self):
        xml = ET.tostring(self.root)
        fw = open(self.vm_name + '.xml', 'w')
        fw.write(xml)

    def create_new_xml(self):
        self.set_image_name()
        self.set_name()
        self.set_uuid()
        self.set_mem_size()
        self.set_cpu_size()
        self.set_source_name()
        self.write_xml()


def main():
    vmmanager = VmManager()
    vmmanager.createByName("SampleCreate", "10", "512", "1")


if __name__ == "__main__":
    main()
