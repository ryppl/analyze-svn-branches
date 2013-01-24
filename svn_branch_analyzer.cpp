// Copyright Dave Abrahams 2013. Distributed under the Boost
// Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
#include "svn_branch_analyzer.hpp"

#include <string>
#include <svn_string.h>
#include <svn_delta.h>
#include <apr_hash.h>
#include <boost/lexical_cast.hpp>
#include <cstring>

namespace ryppl {

static void dump_headers(apr_pool_t* pool, apr_hash_t* headers, char const* prefix)
{
    for (apr_hash_index_t* i = apr_hash_first(pool, headers); i; i = apr_hash_next(i))
    {
        char const* key;
        char const* val;
        apr_hash_this(i, (const void**)&key, NULL, (void**)&val);
        
        std::cout << prefix << "( " << key << ": " << val << ")" << std::endl;
    }
}

// The parser has discovered a new revision record
void svn_branch_analyzer::begin_revision(apr_hash_t *headers, apr_pool_t *pool)
{
    if (char const* rev_text = (char const*)
        apr_hash_get(headers, "Revision-number", APR_HASH_KEY_STRING))
    {
        this->rev_num = boost::lexical_cast<long>(rev_text);
    }
    std::cout << "{ revision: " << this->rev_num << std::endl;
    dump_headers(pool, headers, "  ");    
}

// The parser has discovered a new uuid record
void svn_branch_analyzer::uuid_record(const char *uuid, apr_pool_t *pool)
{
    std::cout << "UUID " << uuid << std::endl;
}

// The parser has discovered a new node record within the current
// revision represented by revision_baton.
void svn_branch_analyzer::begin_node(apr_hash_t *headers, apr_pool_t *pool)
{
    if (char const* kind_txt = (char const*)
        apr_hash_get(headers, "Node-kind", APR_HASH_KEY_STRING))
    {
        this->node_is_dir = (std::strcmp(kind_txt, "dir") == 0);
    }
}
    
// set a named property of the current revision to value. 
void svn_branch_analyzer::set_revision_property(const char *name, const svn_string_t *value)
{
    std::cout << "  [ set-revision-property "
              << name << "=" << std::string(value->data, value->data + value->len)
              << " ]" << std::endl;
}
    
// set a named property of the current node to value. 
void svn_branch_analyzer::set_node_property(const char *name, const svn_string_t *value)
{
    std::cout << "    [ set-node-property "
              << name << "=" << std::string(value->data, value->data + value->len)
              << " ]" << std::endl;
}
    
// delete a named property of the current node
void svn_branch_analyzer::delete_node_property(const char *name)
{
    std::cout << "    [ delete-node-property "
              << name
              << " ]" << std::endl;
    
}
    
// remove all properties of the current node.
void svn_branch_analyzer::remove_node_props()
{
    std::cout << "    [ delete-all-node-properties "
              << " ]" << std::endl;
}
    
void svn_branch_analyzer::write_fulltext_stream(const char *data, apr_size_t *len)
{
    std::cout << "<fulltext: " << *len << "> ";
}

void svn_branch_analyzer::close_fulltext_stream()
{
    std::cout << "<EOS>" << std::endl;
}

void svn_branch_analyzer::apply_textdelta(svn_txdelta_window_t *window)
{
    if (!window)
    {
        std::cout << "    [ textdelta (NULL) ]" << std::endl;
    }
    else
    {
        std::cout << "    [ textdelta " << std::endl;

        std::cout << "        sview_offset: " << window->sview_offset
                  << " sview_len: " << window->sview_len
                  << " tview_len: " << window->tview_len
                  << std::endl;
    
        std::cout << "      num_ops: " << window->num_ops
                  << " src_ops: " << window->src_ops << std::endl;
    
        std::cout << "    ]" << std::endl;
    }
}
    
// The parser has reached the end of the current node
void svn_branch_analyzer::end_node()
{
    std::cout << "  }" << std::endl;
}
    
// The parser has reached the end of the current revision
void svn_branch_analyzer::end_revision()
{
    std::cout << "}" << std::endl;
}

}
