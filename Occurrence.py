# -*- coding: utf8 -*-

###########################################################################
#   This is the package latexparser
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################

# copyright (c) Laurent Claessens, 2010,2012-2016
# email: laurent@claessens-donadello.eu

class Occurrence(object):
    """
    self.as_written : the code as it appears in the file, including \MyMacro, including the backslash.
    self.position : the position at which this occurrence appears. 
        Example, if we look at the LatexCode

        Hello word, \MyMacro{first} 
        and then \MyMacro{second}

        the first occurrence of \MyMacro has position=12
    """
    def __init__(self,name,arguments,as_written="",position=0):
        self.arguments = arguments
        self.number_of_arguments = len(arguments)
        self.name = name
        self.as_written = as_written
        self.arguments_list = arguments
        self.position = position
    def configuration(self):
        r"""
        Return the way the arguments are separated in as_written.
 
        Example, if we have
        \MyMacro<space>{A}<tab>{B}
        {C},
        we return the list
        ["<space>","tab","\n"]

        The following has to be true:
        self.as_written == self.name+self.configuration()[0]+self.arguments_list[0]+etc.
        """
        l=[]
        a = self.as_written.split(self.name)[1]
        for arg in self.arguments_list:
            split = a.split("{"+arg+"}")
            separator=split[0]
            try:
                a=split[1]
            except IndexError:
                print(self.as_written)
                raise
            l.append(separator)
        return l
    def change_argument(self,num,func):
        r"""
        Apply the function <func> to the <n>th argument of self. Then return a new object.
        """
        n=num-1     # Internally, the arguments are numbered from 0.
        arguments=self.arguments_list
        configuration=self.configuration()
        arguments[n]=func(arguments[n])
        new_text=self.name
        if len(arguments) != len(configuration):
            print("Error : length of the configuration list has to be the same as the number of arguments")
            raise ValueError
        for i in range(len(arguments)):
            new_text=new_text+configuration[i]+"{"+arguments[i]+"}"
        return Occurrence(self.name,arguments,new_text,self.position)
    def analyse(self):
        return globals()["Occurrence_"+self.name[1:]](self)     # We have to remove the initial "\" in the name of the macro.
    def __getitem__(self,a):
        return self.arguments[a]
    def __str__(self):
        return self.as_written

class Occurrence_newlabel(object):
    r"""
    takes an occurrence of \newlabel and creates an object which contains the information.

    In the self.section_name we remove "\relax" from the string.
    """
    def __init__(self,occurrence):
        self.occurrence = occurrence
        self.arguments = self.occurrence.arguments
        if len(self.arguments) == 0 :
            self.name = "Non interesting; probably the definition"
            self.listoche = [None,None,None,None,None]
            self.value,self.page,self.section_name,self.fourth,self.fifth=(None,None,None,None,None)
        else :
            self.name = self.arguments[0][0]
            self.listoche = [a[0] for a in SearchArguments(self.arguments[1][0],5)[0]]
            self.value = self.listoche[0]
            self.page = self.listoche[1]
            self.section_name = self.listoche[2].replace(r"\relax","")
            self.fourth = self.listoche[3]      # I don't know the role of the fourth argument of \newlabel
            self.fifth = self.listoche[4]       # I don't know the role of the fifth argument of \newlabel

class Occurrence_cite(object):
    def __init__(self,occurrence):
        self.label = occurrence[0]
    def entry(self,codeBibtex):
        return codeBibtex[self.label]

class Occurrence_newcommand(object):
    def __init__(self,occurrence):
        self.occurrence = occurrence
        self.number_of_arguments = 0
        if self.occurrence[1][1] == "[]":
            self.number_of_arguments = self.occurrence[1][0]
        self.name = self.occurrence[0][0]#[0]
        self.definition = self.occurrence[-1][0]

class Occurrence_label(object):
    def __init__(self,occurence):
        self.occurence=occurence
        self.label=self.occurence.arguments[0]
class Occurrence_ref(object):
    def __init__(self,occurence):
        self.occurence=occurence
        self.label=self.occurence.arguments[0]
class Occurrence_eqref(object):
    def __init__(self,occurence):
        self.occurence=occurence
        self.label=self.occurence.arguments[0]

class Occurrence_input(Occurrence):
    def __init__(self,occurrence):
        Occurrence.__init__(self,occurrence.name,occurrence.arguments,as_written=occurrence.as_written,position=occurrence.position)
        self.occurrence = occurrence
        self.filename = self.occurrence[0]
        self._substitution_text=None        # Make substitution_text "lazy"
    def substitution_text(self):
        if self._substitution_text == None:
            filename=self.filename
            strict_filename = filename
            if "." not in filename:
                strict_filename=filename+".tex"
            try:
                text = "".join( codecs.open(strict_filename,"r",encoding="utf8") )[:-1]    # Without [:-1] I got an artificial empty line at the end.
            except IOError :
                print("Warning : file %s not found."%strict_filename)
                raise
            self._substitution_text=text
        return self._substitution_text

