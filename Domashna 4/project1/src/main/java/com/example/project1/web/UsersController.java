package com.example.project1.web;

import com.example.project1.service.UsersService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
public class UsersController {
    private final UsersService usersService;

    public UsersController(UsersService usersService) {
        this.usersService = usersService;
    }

    @GetMapping("/register")
    public String getRegisterPage() {
        return "register";
    }

    @GetMapping("/login")
    public String getLoginPage() {
        return "login";
    }

    @PostMapping("/register")
    public String addUser(@RequestParam(name = "username") String username,
                          @RequestParam(name = "password") String password,
                          Model model) {
        try {
            usersService.addUser(username, password);
            return "redirect:/login";
        } catch (Exception e) {
            model.addAttribute("text", "Username already exists");
            return "register";
        }
    }
}
