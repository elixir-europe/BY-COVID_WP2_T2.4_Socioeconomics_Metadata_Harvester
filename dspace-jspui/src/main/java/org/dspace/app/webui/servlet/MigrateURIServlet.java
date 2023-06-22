package org.dspace.app.webui.servlet;

import java.io.IOException;
import java.sql.SQLException;
import java.util.Iterator;
import java.util.UUID;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.log4j.Logger;
import org.dspace.authorize.AuthorizeException;
import org.dspace.content.Collection;
import org.dspace.content.Item;
import org.dspace.content.factory.ContentServiceFactory;
import org.dspace.content.service.CollectionService;
import org.dspace.content.service.ItemService;
import org.dspace.core.Context;
import org.dspace.services.ConfigurationService;
import org.dspace.services.factory.DSpaceServicesFactory;

public class MigrateURIServlet extends DSpaceServlet {
    private static final Logger log = Logger.getLogger(MigrateURIServlet.class);

    protected ConfigurationService configurationService = DSpaceServicesFactory.getInstance().getConfigurationService();

    private final transient ItemService itemService = ContentServiceFactory.getInstance().getItemService();

    private final transient CollectionService collectionService = ContentServiceFactory.getInstance()
            .getCollectionService();

    @Override
    protected void doDSGet(Context context, HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException, SQLException, AuthorizeException {

        String collectionId = request.getParameter("collectionId");
        Collection collection = collectionService.find(context, UUID.fromString(collectionId));

        Iterator<Item> items = itemService.findByCollection(context, collection);

        while (items.hasNext()) {
            Item currentItem = items.next();
            String uri = itemService.getMetadataFirstValue(currentItem, "dc", "identifier", "uri", "en");
            int counter = 1;
            if (uri == null) {
                String nuri = "	https://t2-4.bsc.es/jspui/handle/" + currentItem.getHandle();
                log.error("[#"+counter+"] Migrating URI for item: " + currentItem.getHandle());
                itemService.addMetadata(context, currentItem, "dc", "identifier", "uri", Item.ANY, nuri);
                itemService.update(context, currentItem);
                counter++;

            }
        }
        context.commit();
    }

}
