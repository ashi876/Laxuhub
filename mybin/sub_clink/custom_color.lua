
function my_prompt_filter()
    local username = os.getenv("USERNAME")
    local computername = os.getenv("COMPUTERNAME") 
    local cwd = clink.get_cwd():gsub('\\', '/')
    clink.prompt.value = "\x1b[1;32m"..username.."@"..computername.."\x1b[0m \x1b[1;33m"..cwd.."\x1b[0m\n\x1b[1;32m$\x1b[0m "
end

clink.prompt.register_filter(my_prompt_filter, 1)
