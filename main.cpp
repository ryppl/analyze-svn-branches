// Copyright Dave Abrahams 2013. Distributed under the Boost
// Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#include "svn_failure.hpp"
#include "svn_branch_analyzer.hpp"
#include <exception>
#include <iostream>
#include <svn_pools.h>
#include <svn_io.h>
#include <svn_fs.h>

namespace ryppl {

// Adapted from subversion/svndumpfilter/main.c
static svn_stream_t*
create_stdio_stream(
    APR_DECLARE(apr_status_t) open_fn(apr_file_t **, apr_pool_t *),
    apr_pool_t *pool)
{
  apr_file_t *stdio_file;
  apr_status_t apr_err = open_fn(&stdio_file, pool);

  if (apr_err)
      check_svn_failure(svn_error_wrap_apr(apr_err, "Can't open stdio file"));

  return svn_stream_from_aprfile2(stdio_file, TRUE, pool);
}

}

int main()
{
    // Create our top-level pool.
    apr_initialize();
    apr_allocator_t *allocator;
    if (apr_allocator_create(&allocator))
        return EXIT_FAILURE;

    apr_allocator_max_free_set(allocator, SVN_ALLOCATOR_RECOMMENDED_MAX_FREE);

    apr_pool_t *pool;
    pool = svn_pool_create_ex(NULL, allocator);
    apr_allocator_owner_set(allocator, pool);

    int exit_code = EXIT_FAILURE;
    try
    {
        ryppl::check_svn_failure(svn_fs_initialize(pool));
        ryppl::svn_branch_analyzer parse(pool);
        
        parse(ryppl::create_stdio_stream(apr_file_open_stdin, pool));
        exit_code = EXIT_SUCCESS;
    }
    catch(ryppl::svn_failure const& x)
    {
        std::cerr << "Failed with svn error: " << x.what() << std::endl;
    }
    catch(std::exception const& x)
    {
        std::cerr << "Failed with std::exception: " << x.what() << std::endl;
    }
    catch(...)
    {
        std::cerr << "Failed with unknown exception" << std::endl;
    }
    
    svn_pool_destroy(pool);
    return exit_code;
}

