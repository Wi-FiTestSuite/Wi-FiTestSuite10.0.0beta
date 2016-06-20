###############################################################################
#
# Copyright (c) 2016 Wi-Fi Alliance
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE
# USE OR PERFORMANCE OF THIS SOFTWARE.
#
###############################################################################

#!/usr/bin/env python
﻿import re


class Node(object):
    """The node class whose object is to be stored on the linkedlist.

    Attributes:
        data (dictionary): The dictionary to store the key/value of script keywords.
        next (Node): The next node.
        tag (str): The tag to distinguish the attribute of each node.
        group_tag (str): The tag to identify the calling loop found in the scripts.

    """
    def __init__(self, tag, group_tag, next_node):
        self.data = {}
        self.next = next_node
        self.tag = tag
        self.group_tag = group_tag



class SingleLinkedList(object):
    """A Singly linked list class to store node objects.

    Attributes:
        head (Node): The head node.
        tail (Node): The tail node.

    """
    def __init__(self):
        self.head = None
        self.tail = None


    def insert(self, key, value, tag="", group_tag=""):
        """Inserts a node to the linkedlist with the key, tag and group_tag.

        Args:
            key (str): The key to uniquely identify the node.
            tag (str): The tag to label the node's attribute.
            group_tag (str): The group tag.
        """
        node = Node(tag, group_tag, None)
        node.data[key] = value

        if self.head is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
        self.tail = node


    def delete(self, node_key):
        """Deletes a node from the linkedlist based on the specified key.

        Args:
            node_key (str): The node key.
        """
        curr_node = self.head
        prev_node = None

        while curr_node is not None:
            if list[curr_node.data.keys()][0] == node_key:
                if prev_node is not None:
                    prev_node.next = curr_node.next
                else:
                    self.head = curr_node.next
            prev_node = curr_node
            curr_node = curr_node.next


    def size(self):
        """The size of the linkedlist.
        """
        curr_node = self.head
        count = 0
        while curr_node:
            count += 1
            curr_node = curr_node.next
        return count


    def get_num_nodes_with_keyword(self, parent_node_key, keyword):
        """Gets the number of nodes associated with the given keyword.

        Args:
            keyword (str): The key name to match with.
        """
        count = []
        curr_node = self.head

        while curr_node:
            key_list = curr_node.data.keys()
            key_count = len(key_list)
            if key_count == 1 and key_list[0] == parent_node_key:
                curr_node = curr_node.next
                key_name = curr_node.data.keys()[0]
                while curr_node.data.values()[0] != "":
                    if re.search(keyword, key_name, re.I):
                        #count += 1
                        count.append(key_name)
                        curr_node = curr_node.next
                        if curr_node is None:
                            break
                        key_name = curr_node.data.keys()[0]
                    else:
                        curr_node = curr_node.next
                        if curr_node is None:
                            break
                        key_name = curr_node.data.keys()[0]
                break
            else:
                curr_node = curr_node.next

        return count


    def get_next_node(self, curr_node_key):
        """Gets the next node of currently found node with the specified key.

        Args:
            curr_node_key (str): The key to search for the current node.
        """
        curr_node = self.head

        while curr_node:
            key_list = curr_node.data.keys()
            key_count = len(key_list)
            if key_count == 1 and key_list[0] == curr_node_key:
                curr_node = curr_node.next
                break
            else:
                curr_node = curr_node.next
        if curr_node is None:
            #raise ValueError("Data not in the list")
            return None
        return curr_node


    def search_node_by_parent(self, parent_node_key, child_node_key):
        """Searches for the child node by given its node key and its parent node key.

        Args:
            parent_node_key (str): The parent node key.
            child_node_key (str): The child node key.
        """
        curr_node = self.head
        found = False
        child_found = False
        while curr_node and found is False:
            if (curr_node.data.keys())[0] == parent_node_key:
                # to make sure the corresponding parent xml element has not nodevalue but just a parent element
                # for example, <STA><c1>0</c1></STA>
                value = "%s" % curr_node.data[parent_node_key]
                value = value.strip()
                if not value:
                    found = True
                else:
                    curr_node = curr_node.next
                    continue

                curr_node = curr_node.next
                while curr_node and child_found is False:
                    if (curr_node.data.keys())[0] == child_node_key:
                        child_found = True
                        return curr_node
                    else:
                        curr_node = curr_node.next
                        value1 = curr_node.data[curr_node.data.keys()[0]]
                        value1 = value1.strip()
                        if value1 == "":
                            break

                ##->print "(%s:%s) not found in the list" % (parent_node_key, child_node_key)
                return None
            else:
                curr_node = curr_node.next
        if curr_node is None:
            #raise ValueError("Data not in the list")
            return None
        return curr_node


    def search(self, node_key):
        """Searches for a node given its key.

        Args:
            node_key (str): The node key.
        """
        curr_node = self.head
        found = False
        while curr_node and found is False:
            key_list = curr_node.data.keys()
            key_count = len(key_list)
            if key_count == 1 and key_list[0] == node_key:
                found = True
                break
            else:
                curr_node = curr_node.next
        if curr_node is None:
            #raise ValueError("Data not in the list")
            return None
        return curr_node
