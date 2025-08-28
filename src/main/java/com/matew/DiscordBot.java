package com.matew;

import org.slf4j.LoggerFactory;
import com.matew.config.BotConfig;
import net.dv8tion.jda.api.JDA;
import net.dv8tion.jda.api.JDABuilder;
import net.dv8tion.jda.api.requests.GatewayIntent;
import net.dv8tion.jda.api.interactions.commands.OptionType;
import net.dv8tion.jda.api.interactions.commands.build.Commands;
import net.dv8tion.jda.api.interactions.commands.Command;

import java.util.EnumSet;

public class DiscordBot {
    private static final org.slf4j.Logger logger = LoggerFactory.getLogger(DiscordBot.class);
    private static JDA jda;

    public static void main(String[] args) {
        String botToken = BotConfig.getBotToken();

        if (botToken == null || botToken.isEmpty()) {
            logger.error("Bot token is not configured. Please set the botToken in config.properties.");
            return;
        }

        try {
            jda = JDABuilder.createDefault(botToken)
                    .enableIntents(EnumSet.allOf(GatewayIntent.class))
                    .addEventListeners(new CommandListener())
                    .build();
            jda.awaitReady();
            logger.info("bot up and running");
            
            registerCommands();
        } catch (Exception e) {
            logger.error("Error initializing JDA", e);
        }
    }

    private static void registerCommands() {
        if (jda == null) {
            logger.error("JDA is not initialized. Cannot register commands.");
            return;
        }
        jda.updateCommands()
                .addCommands(
                        Commands.slash("ping", "Checks the bot's latency to Discord's gateway."),
                        Commands.slash("info", "Displays information about the bot."),
                        Commands.slash("echo", "Echoes back your message.")
                                .addOption(OptionType.STRING, "message", "The message to echo back", true))
                .queue(
                    success -> logger.info("Commands registered successfully."),
                    error -> logger.error("Failed to register commands.", error));
    }
}