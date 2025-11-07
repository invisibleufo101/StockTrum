//package com.stocktrum.backend.core.aspect;
//
//import com.stocktrum.backend.features.auth.api.dto.UserRegisterDTO;
//import com.stocktrum.backend.features.user.repo.UserRepository;
//import org.aspectj.lang.annotation.Aspect;
//import org.aspectj.lang.annotation.Before;
//import org.springframework.stereotype.Component;
//
//@Aspect
//@Component
//public class Validation {
//  private final UserRepository userRepository;
//
//  public Validation(UserRepository userRepository) {
//    this.userRepository = userRepository;
//  }
//
//  @Before("execution(* com.stocktrum.backend.features.user.api.UserController.register(..)) && args(userDto,..)")
//  public void EmailDuplicationCheck(UserRegisterDTO userDto) {
//    String email = userDto.getEmail();
//    if (userRepository.existsByEmail(email)) {
//      throw new IllegalArgumentException("Email already in use");
//    }
//  }
//
//}
