package com.matew.config;

import org.slf4j.LoggerFactory;

import java.io.IOException; 
import java.io.InputStream;
import java.util.Properties;


public class BotConfig {
  private static final org.slf4j.Logger logger = LoggerFactory.getLogger(BotConfig.class);
  private static final String CONFIG_FILE = "config.properties";
  private static final Properties properties = new Properties();

  static {
    try (InputStream input = BotConfig.class.getClassLoader().getResourceAsStream(CONFIG_FILE)) {
      if (input == null) {
        logger.error("config file not found lmao" + CONFIG_FILE);
      } else {
        properties.load(input);
        logger.info("config loaded from {}" + CONFIG_FILE);
      }
    } catch (IOException ex) {
      logger.error("Error loading configuration file", ex);
    }   
  }

  public static String getBotToken() {
    return properties.getProperty("botToken");
  }
}
