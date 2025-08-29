package com.matew.commands;

import net.dv8tion.jda.api.events.interaction.command.SlashCommandInteractionEvent;

public class PingCommand implements Command {
    @Override
    public String getName() {
        return "ping";
    }

    @Override
    public String getDescription() {
        return "Checks the bot's latency to Discord's gateway.";
    }

    @Override
    public void executeSlash(SlashCommandInteractionEvent event) {
        long ping = event.getJDA().getGatewayPing();
        event.reply("Pong! Latency: " + ping + "ms").queue();
    }

}
