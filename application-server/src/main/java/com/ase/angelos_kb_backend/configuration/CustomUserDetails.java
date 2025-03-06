package com.ase.angelos_kb_backend.configuration;

import com.ase.angelos_kb_backend.model.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.GrantedAuthority;

import java.util.Collection;
import java.util.Collections;

public class CustomUserDetails implements UserDetails {

    private final User user;

    public CustomUserDetails(User user) {
        this.user = user;
    }

    public Long getOrgId() {
        return user.getOrganisation().getOrgID();
    }

    public boolean isSystemAdmin() {
        return user.isSystemAdmin();
    }

    public boolean isAdmin() {
        return user.isAdmin();
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        // Implement roles if needed
        return Collections.emptyList();
    }

    @Override
    public String getPassword() {
        return user.getPassword();
    }

    @Override
    public String getUsername() {
        return user.getMail();
    }

    @Override
    public boolean isAccountNonExpired() {
        return true; // Modify based on your logic
    }

    @Override
    public boolean isAccountNonLocked() {
        return true; // Modify based on your logic
    }

    @Override
    public boolean isCredentialsNonExpired() {
        return true; // Modify based on your logic
    }

    @Override
    public boolean isEnabled() {
        return user.isApproved(); // Or true if all users are enabled
    }
}
