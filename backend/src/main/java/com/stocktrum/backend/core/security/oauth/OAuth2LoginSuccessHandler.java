//package com.stocktrum.backend.core.security.oauth;
//
//import com.stocktrum.backend.core.security.jwt.JWTService;
//import com.stocktrum.backend.features.user.domain.User;
//import com.stocktrum.backend.features.user.repo.UserRepository;
//import jakarta.servlet.ServletException;
//import jakarta.servlet.http.HttpServletRequest;
//import jakarta.servlet.http.HttpServletResponse;
//import org.springframework.beans.factory.annotation.Autowired;
//import org.springframework.security.core.Authentication;
//import org.springframework.security.core.userdetails.UsernameNotFoundException;
//import org.springframework.security.oauth2.core.user.OAuth2User;
//import org.springframework.security.web.authentication.AuthenticationSuccessHandler;
//import org.springframework.stereotype.Component;
//
//import java.io.IOException;
//import java.util.Optional;
//
//@Component
//public class OAuth2LoginSuccessHandler implements AuthenticationSuccessHandler {
//
//  @Autowired
//  private JWTService jwtService;
//
//  @Autowired
//  private UserRepository userRepository;
//
//  @Override
//  public void onAuthenticationSuccess(HttpServletRequest request, HttpServletResponse response, Authentication authentication) throws IOException, ServletException {
//    OAuth2User oauthUser = (OAuth2User) authentication.getPrincipal();
//    String email = oauthUser.getAttribute("email");
//    Optional<User> user = userRepository.findByEmail(email);
//
//    if (!user.isPresent()) {
//      throw new UsernameNotFoundException("User not found");
//    }
//
//    String jwt = jwtService.generateAccessToken(email);
//    response.setHeader("Authorization", "Bearer " + jwt);
//  }
//
//}
