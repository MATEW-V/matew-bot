package com.matew.listeners;

import com.matew.commands.Command;
import com.matew.commands.EchoCommand;
import com.matew.commands.InfoCommand;
import com.matew.commands.PingCommand;

import net.dv8tion.jda.api.events.interaction.command.SlashCommandInteractionEvent;
import net.dv8tion.jda.api.events.session.ReadyEvent;
import net.dv8tion.jda.api.hooks.ListenerAdapter;
import org.jetbrains.annotations.NotNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashMap;
import java.util.Map;

public class CommandListener extends ListenerAdapter { // extends importnmt
    private static final Logger logger = LoggerFactory.getLogger(CommandListener.class);
    private final Map<String, Command> commands = new HashMap<>(); //commands with an s wtf

    public CommandListener() {
        // Register commands here
        // Example: command.put("ping", new PingCommand());
        commands.put("ping", new PingCommand());
        commands.put("info", new InfoCommand());
        commands.put("echo", new EchoCommand());
        logger.info("Commands registered: " + commands.size());
    }

    @Override
    public void onReady(@NotNull ReadyEvent event) {
        logger.info("jda ready; logged in as:",
                event.getJDA().getSelfUser().getName(),
                event.getJDA().getSelfUser().getDiscriminator());
    }

    @Override
    public void onSlashCommandInteraction(@NotNull SlashCommandInteractionEvent event) {
        String commandName = event.getName();
        Command command = commands.get(commandName); //command no s

        if (command != null) {
            logger.debug("Executing slash command: {} from user: {}", commandName, event.getUser().getName());
            command.executeSlash(event);
        } else {
            logger.warn("Unknown slash command: {} from user: {}", commandName, event.getUser().getName());
            event.reply("Unknown command!").setEphemeral(true).queue(); // Ephemeral reply for unknown commands
        }
    }
}
