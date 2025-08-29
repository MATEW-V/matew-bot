package com.matew.commands;

import net.dv8tion.jda.api.EmbedBuilder;
import net.dv8tion.jda.api.entities.MessageEmbed;
import net.dv8tion.jda.api.events.interaction.command.SlashCommandInteractionEvent;

import java.awt.Color;

public class InfoCommand implements Command {
    @Override
    public String getName() {
        return "info";
    }

    @Override
    public String getDescription() {
        return "Displays information about the bot.";
    }

    @Override
    public void executeSlash(SlashCommandInteractionEvent event) {
        EmbedBuilder embedBuilder = new EmbedBuilder();
        embedBuilder.setTitle("Bot Information");
        embedBuilder.setDescription(
                "This bot is matewsbot; made by mat_ew for mat_ew. All rights reserved.");
        embedBuilder.setColor(new Color(128, 0, 0));
        embedBuilder.addField("Language", "Java", true);
        embedBuilder.addField("Library", "JDA (Java Discord API)", true);
        embedBuilder.setFooter("4 shits andgiggles");

        MessageEmbed embed = embedBuilder.build();
        event.replyEmbeds(embed).queue();
    }

}
