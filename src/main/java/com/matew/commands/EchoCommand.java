package com.matew.commands;

import net.dv8tion.jda.api.interactions.commands.OptionMapping;

public class EchoCommand implements Command {
    @Override
    public String getName() {
        return "echo";
    }

    @Override
    public String getDescription() {
        return "Echoes back your message.";
    }

    @Override
    public void executeSlash(net.dv8tion.jda.api.events.interaction.command.SlashCommandInteractionEvent event) {
        OptionMapping textOption = event.getOption("message");
        String textToEcho = "";
        if (textOption != null) {
            textToEcho = textOption.getAsString();
        } else {
            textToEcho = "nothin givin";
        }
        event.reply(textToEcho).setEphemeral(false).queue();
    }

}
